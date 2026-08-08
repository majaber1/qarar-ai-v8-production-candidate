import json
import queue
import threading
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.audit import record_audit
from app.core.auth import Principal, require_principal, require_roles
from app.core.database import get_db, SessionLocal
from app.core.ratelimit import check_ai_rate_limit, check_budget
from app.models.case import DecisionCase
from app.models.fabric import KnowledgeSource
from app.models.security import DecisionApproval
from app.models.workspace import Project
from app.schemas.case import CaseCreate, CaseResponse, ApprovalRequest
from app.services.advisor import analyze_case
from app.services.clarification import classify_missing_information
from app.services.contracts import CaseInput
from app.services.fabric import ingest_source
from app.services.orchestrator import orchestrator

class ClarificationAnswers(BaseModel):
    answers: dict[str, str]

router = APIRouter(prefix='/cases', tags=['cases'])


def _case_for_tenant(db: Session, case_id: int, tenant_id: str) -> DecisionCase | None:
    return db.scalar(select(DecisionCase).where(DecisionCase.id == case_id, DecisionCase.tenant_id == tenant_id))


@router.post('', response_model=CaseResponse, status_code=201)
def create_case(p: CaseCreate, db: Session = Depends(get_db), principal: Principal = Depends(require_principal)):
    if p.project_id is not None and not db.scalar(select(Project).where(Project.id == p.project_id, Project.tenant_id == principal.tenant_id)):
        raise HTTPException(404, 'Project not found')
    x = DecisionCase(tenant_id=principal.tenant_id, created_by=principal.subject, **p.model_dump())
    db.add(x); db.commit(); db.refresh(x)
    record_audit(principal.tenant_id, principal.subject, 'case_created', auth_type=principal.auth_type,
                 resource_type='case', resource_id=x.id, metadata={'title': x.title, 'project_id': x.project_id})
    return x


@router.get('', response_model=list[CaseResponse])
def list_cases(db: Session = Depends(get_db), principal: Principal = Depends(require_principal)):
    q = select(DecisionCase).where(DecisionCase.tenant_id == principal.tenant_id).order_by(DecisionCase.created_at.desc())
    return list(db.scalars(q).all())


@router.get('/{case_id}', response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db), principal: Principal = Depends(require_principal)):
    x = _case_for_tenant(db, case_id, principal.tenant_id)
    if not x:
        raise HTTPException(404, 'Case not found')
    return x


@router.post('/{case_id}/analyze', response_model=CaseResponse)
def analyze(case_id: int, db: Session = Depends(get_db), principal: Principal = Depends(require_roles('project_manager','developer'))):
    x = _case_for_tenant(db, case_id, principal.tenant_id)
    if not x:
        raise HTTPException(404, 'Case not found')
    ok, reason = check_budget(principal.tenant_id)
    if not ok:
        raise HTTPException(429, reason)
    ok, reason = check_ai_rate_limit(principal.subject)
    if not ok:
        raise HTTPException(429, reason)
    r = analyze_case(x.id, x.title, x.description, x.urgency, x.category, x.language, principal.tenant_id)
    x.selected_agents=r['selected_agents']; x.skipped_agents=r['skipped_agents']; x.agent_results=r['agent_results']
    x.analysis=r['analysis']; x.audit_log=r['audit_log']; x.analysis_source=r['analysis_source']

    # Intelligent clarification gate: only surface it the FIRST time (once the PM has answered,
    # x.clarification_answers is set and we don't re-block on the same unresolved unknowns forever).
    unknowns = (r['analysis'] or {}).get('unknowns') or []
    if unknowns and not x.clarification_answers:
        gate = classify_missing_information(unknowns, principal.tenant_id, x.id)
        if gate['top_questions']:
            x.pending_clarifications = gate['top_questions']
            x.status = 'needs_clarification'
        else:
            x.status = 'recommendation_ready'
    else:
        x.status = 'recommendation_ready'

    db.commit(); db.refresh(x)
    record_audit(principal.tenant_id, principal.subject, 'case_analyzed', auth_type=principal.auth_type,
                 resource_type='case', resource_id=x.id,
                 metadata={'selected_agents': r['selected_agents'], 'analysis_source': r['analysis_source'], 'status': x.status})
    return x


@router.post('/{case_id}/clarify', response_model=CaseResponse)
def clarify(case_id: int, req: ClarificationAnswers, db: Session = Depends(get_db),
            principal: Principal = Depends(require_roles('project_manager', 'developer'))):
    x = _case_for_tenant(db, case_id, principal.tenant_id)
    if not x:
        raise HTTPException(404, 'Case not found')
    if not req.answers:
        raise HTTPException(400, 'At least one answer is required')
    x.clarification_answers = {**(x.clarification_answers or {}), **req.answers}
    x.pending_clarifications = None
    x.status = 'recommendation_ready'
    db.commit()

    # Answers become organizational evidence (Trust B) so the next analysis run can see them.
    note = '\n'.join(f'{q}\n{a}' for q, a in req.answers.items())
    from app.services.object_storage import storage
    key = storage().put(f'clarification-{case_id}.txt', note.encode('utf-8'))
    src = KnowledgeSource(tenant_id=principal.tenant_id, case_id=case_id, source_type='clarification',
                          title=f'PM clarification for case {case_id}', source_ref='clarification-gate',
                          object_key=key, trust_level='B', status='queued')
    db.add(src); db.commit(); db.refresh(src)
    ingest_source(src.id)

    db.refresh(x)
    record_audit(principal.tenant_id, principal.subject, 'case_clarified', auth_type=principal.auth_type,
                 resource_type='case', resource_id=x.id, metadata={'questions_answered': list(req.answers.keys())})
    return x


@router.post('/{case_id}/analyze-stream')
def analyze_stream(case_id: int, principal: Principal = Depends(require_roles('project_manager','developer'))):
    tenant_id = principal.tenant_id
    with SessionLocal() as db:
        x = _case_for_tenant(db, case_id, tenant_id)
        if not x:
            raise HTTPException(404, 'Case not found')
        ok, reason = check_budget(tenant_id)
        if not ok:
            raise HTTPException(429, reason)
        ok, reason = check_ai_rate_limit(principal.subject)
        if not ok:
            raise HTTPException(429, reason)
        case = CaseInput(x.id, x.title, x.description, x.urgency, x.category, x.language, tenant_id)

    events: queue.Queue = queue.Queue()
    done = object()

    def emit(event: dict):
        events.put(event)

    def worker():
        try:
            result = orchestrator.analyze(case, event_callback=emit)
            with SessionLocal() as db:
                target = _case_for_tenant(db, case_id, tenant_id)
                if target:
                    target.selected_agents=result['selected_agents']; target.skipped_agents=result['skipped_agents']
                    target.agent_results=result['agent_results']; target.analysis=result['analysis']; target.audit_log=result['audit_log']
                    target.analysis_source=result['analysis_source']
                    unknowns=(result['analysis'] or {}).get('unknowns') or []
                    gate=classify_missing_information(unknowns,tenant_id,target.id) if unknowns and not target.clarification_answers else {'top_questions':[]}
                    target.pending_clarifications=gate['top_questions'] or None
                    target.status='needs_clarification' if gate['top_questions'] else 'recommendation_ready'
                    db.commit()
                    record_audit(tenant_id, principal.subject, 'case_analyzed_stream', auth_type=principal.auth_type,
                                 resource_type='case', resource_id=target.id, metadata={'status':target.status})
        except Exception as exc:
            emit({'type':'fatal_error','message':str(exc)})
        finally:
            events.put(done)

    threading.Thread(target=worker, daemon=True).start()

    def stream():
        while True:
            item = events.get()
            if item is done:
                break
            yield json.dumps(item, ensure_ascii=False) + '\n'

    return StreamingResponse(
        stream(),
        media_type='application/x-ndjson',
        headers={'Cache-Control':'no-cache, no-transform','X-Accel-Buffering':'no'},
    )


@router.post('/{case_id}/approve', response_model=CaseResponse)
def approve(case_id: int, p: ApprovalRequest, db: Session = Depends(get_db), principal: Principal = Depends(require_roles('executive'))):
    x = _case_for_tenant(db, case_id, principal.tenant_id)
    if not x or not x.analysis:
        raise HTTPException(404, 'Analyzed case not found')
    if p.option_id not in {o.get('id') for o in x.analysis.get('options', [])}:
        raise HTTPException(400, 'Invalid option')
    x.approved_option=p.option_id; x.decision_owner=p.decision_owner; x.due_date=p.due_date; x.status='approved'
    db.add(DecisionApproval(
        tenant_id=principal.tenant_id,
        case_id=x.id,
        option_id=p.option_id,
        decision_owner=p.decision_owner,
        approved_by=principal.subject,
        status='approved',
    ))
    db.commit(); db.refresh(x)
    record_audit(principal.tenant_id, principal.subject, 'case_approved', auth_type=principal.auth_type,
                 resource_type='case', resource_id=x.id,
                 metadata={'option_id': p.option_id, 'decision_owner': p.decision_owner})
    return x
