import json
import queue
import threading
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.audit import record_audit
from app.core.auth import Principal, require_principal, require_roles
from app.core.database import get_db, SessionLocal
from app.core.ratelimit import check_ai_rate_limit, check_budget
from app.models.case import DecisionAction, DecisionCase, DecisionOutcome
from app.models.fabric import KnowledgeSource
from app.models.security import DecisionApproval
from app.models.workspace import Project
from app.schemas.case import (
    CaseCreate, CaseResponse, CaseTransitionRequest, CaseUpdate,
    ApprovalRequest, ScoreOverrideRequest
)
from app.services.advisor import analyze_case
from app.services.clarification import classify_missing_information
from app.services.contracts import CaseInput
from app.services.fabric import ingest_source
from app.services.orchestrator import orchestrator
from app.services.tools.scoring import (
    normalize_criteria, normalize_weights, sensitivity_analysis,
    score_options, compose_confidence, DECISION_TEMPLATES, SCENARIO_PRESETS
)

class ClarificationAnswers(BaseModel):
    answers: dict[str, str]

class SensitivityRequest(BaseModel):
    weight_changes:dict[str,float]={}
    score_changes:dict[str,dict[str,float]]={}

class ActionCreate(BaseModel):
    title:str
    description:str|None=None
    owner:str
    status:str='not_started'
    priority:str='medium'
    due_date:date|None=None
    dependency_id:int|None=None
    source_reference:str|None=None
    notes:str|None=None

class ActionUpdate(BaseModel):
    title:str|None=None;description:str|None=None;owner:str|None=None;status:str|None=None
    priority:str|None=None;due_date:date|None=None;dependency_id:int|None=None;notes:str|None=None

class OutcomeCreate(BaseModel):
    result:str
    expected_result:str
    actual_result:str
    lessons_learned:str|None=None
    corrective_action:str|None=None
    next_review_date:date|None=None

router = APIRouter(prefix='/cases', tags=['cases'])


def _case_for_tenant(db: Session, case_id: int, tenant_id: str) -> DecisionCase | None:
    return db.scalar(select(DecisionCase).where(DecisionCase.id == case_id, DecisionCase.tenant_id == tenant_id))


@router.get('/templates')
def get_templates():
    return DECISION_TEMPLATES


@router.get('/scenarios/presets')
def get_scenario_presets():
    return SCENARIO_PRESETS


@router.get('/follow-up/summary')
def follow_up_summary(db: Session = Depends(get_db), principal: Principal = Depends(require_principal)):
    actions = list(db.scalars(select(DecisionAction).where(DecisionAction.tenant_id == principal.tenant_id)).all())
    today = date.today()
    return {
        'open_actions': sum(x.status not in {'completed', 'cancelled'} for x in actions),
        'overdue_actions': sum(
            bool(x.due_date and x.due_date < today and x.status not in {'completed', 'cancelled'}) for x in actions
        ),
        'completed_actions': sum(x.status == 'completed' for x in actions),
    }


@router.post('', response_model=CaseResponse, status_code=201)
def create_case(p: CaseCreate, db: Session = Depends(get_db), principal: Principal = Depends(require_principal)):
    if p.project_id is not None and not db.scalar(select(Project).where(Project.id == p.project_id, Project.tenant_id == principal.tenant_id)):
        raise HTTPException(404, 'Project not found')
    values = p.model_dump()
    if values.get('scoring_weights') is not None:
        try:
            values['scoring_weights'] = normalize_weights(values['scoring_weights'])
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
    if values.get('scoring_criteria') is not None:
        try: values['scoring_criteria']=normalize_criteria(values['scoring_criteria'])
        except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    if values.get('scoring_criteria') is None: values['scoring_criteria']=normalize_criteria(None,values.get('scoring_weights'))
    x = DecisionCase(tenant_id=principal.tenant_id, created_by=principal.subject, status='draft', **values)
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


@router.patch('/{case_id}', response_model=CaseResponse)
def update_case(case_id: int, payload: CaseUpdate, db: Session = Depends(get_db),
                principal: Principal = Depends(require_roles('project_manager', 'developer'))):
    case = _case_for_tenant(db, case_id, principal.tenant_id)
    if not case:
        raise HTTPException(404, 'Case not found')
    if case.status in {'approved', 'archived'}:
        raise HTTPException(409, 'Approved or archived cases must be reopened before editing')
    values = payload.model_dump(exclude_unset=True)
    if 'project_id' in values and values['project_id'] is not None and not db.scalar(
        select(Project).where(Project.id == values['project_id'], Project.tenant_id == principal.tenant_id)
    ):
        raise HTTPException(404, 'Project not found')
    if values.get('scoring_weights') is not None:
        try:
            values['scoring_weights'] = normalize_weights(values['scoring_weights'])
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
    if values.get('scoring_criteria') is not None:
        try: values['scoring_criteria']=normalize_criteria(values['scoring_criteria'])
        except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    for field, value in values.items():
        setattr(case, field, value)
    db.commit(); db.refresh(case)
    record_audit(principal.tenant_id, principal.subject, 'case_updated', auth_type=principal.auth_type,
                 resource_type='case', resource_id=case.id, metadata={'fields': sorted(values)})
    return case


@router.post('/{case_id}/transition', response_model=CaseResponse)
def transition_case(case_id: int, payload: CaseTransitionRequest, db: Session = Depends(get_db),
                    principal: Principal = Depends(require_roles('project_manager', 'developer', 'executive'))):
    case = _case_for_tenant(db, case_id, principal.tenant_id)
    if not case:
        raise HTTPException(404, 'Case not found')
    target_status='reopened' if payload.status=='open' else payload.status
    if target_status in {'approved','rejected'} and 'executive' not in principal.roles:
        raise HTTPException(403, 'Only an executive can approve or reject a recommendation')
    allowed = {
        'open': {'ready_for_analysis','deferred','archived'}, 'draft': {'ready_for_analysis','deferred','archived'},
        'needs_clarification': {'needs_information','ready_for_analysis','deferred','archived'},
        'needs_information': {'ready_for_analysis','deferred','archived'},
        'ready_for_analysis': {'analyzing','deferred','archived'}, 'analyzing': {'recommendation_ready','needs_information'},
        'recommendation_ready': {'pending_approval','rejected','deferred','archived'},
        'pending_approval': {'approved','rejected','deferred','archived'},
        'approved': {'reopened','archived'}, 'rejected': {'reopened','archived'},
        'deferred': {'reopened','archived'}, 'reopened': {'ready_for_analysis','deferred','archived'},
        'archived': {'reopened'},
    }
    if target_status not in allowed.get(case.status, set()):
        raise HTTPException(409, f'Cannot transition case from {case.status} to {target_status}')
    previous = case.status
    case.status = target_status
    if target_status == 'reopened':
        case.approved_option = None
        case.decision_owner = None
        case.due_date = None
    db.commit(); db.refresh(case)
    record_audit(principal.tenant_id, principal.subject, 'case_status_changed', auth_type=principal.auth_type,
                 resource_type='case', resource_id=case.id,
                 metadata={'from': previous, 'to': target_status, 'reason': payload.reason})
    return case


@router.post('/{case_id}/analyze', response_model=CaseResponse)
def analyze(case_id: int, db: Session = Depends(get_db), principal: Principal = Depends(require_roles('project_manager','developer'))):
    x = _case_for_tenant(db, case_id, principal.tenant_id)
    if not x:
        raise HTTPException(404, 'Case not found')
    if x.status not in {'draft','open','reopened','ready_for_analysis','needs_information','needs_clarification','recommendation_ready'}:
        raise HTTPException(409,'Case must be reopened before analysis')
    ok, reason = check_budget(principal.tenant_id)
    if not ok:
        raise HTTPException(429, reason)
    ok, reason = check_ai_rate_limit(principal.subject)
    if not ok:
        raise HTTPException(429, reason)
    previous=x.status;x.status='analyzing';db.commit()
    r = analyze_case(x.id, x.title, x.description, x.urgency, x.category, x.language, principal.tenant_id, x.scoring_weights, x.scoring_criteria, options=x.options)
    x.selected_agents=r['selected_agents']; x.skipped_agents=r['skipped_agents']; x.agent_results=r['agent_results']
    x.analysis=r['analysis']; x.audit_log=r['audit_log']; x.analysis_source=r['analysis_source'];x.calculation_metadata=(r['analysis'] or {}).get('calculation_metadata')
    x.options = r.get('options')
    x.score_provenance = r.get('score_provenance')

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
    x.status = 'ready_for_analysis'
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
        if x.status not in {'draft','open','reopened','ready_for_analysis','needs_information','needs_clarification','recommendation_ready'}:
            raise HTTPException(409, 'Case must be reopened before analysis')
        ok, reason = check_budget(tenant_id)
        if not ok:
            raise HTTPException(429, reason)
        ok, reason = check_ai_rate_limit(principal.subject)
        if not ok:
            raise HTTPException(429, reason)
        x.status = 'analyzing'
        db.commit()
        case = CaseInput(x.id, x.title, x.description, x.urgency, x.category, x.language, tenant_id,
                         scoring_weights=x.scoring_weights, scoring_criteria=x.scoring_criteria, options=x.options)

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
                    target.analysis_source=result['analysis_source'];target.calculation_metadata=(result['analysis'] or {}).get('calculation_metadata')
                    target.options = result.get('options')
                    target.score_provenance = result.get('score_provenance')
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


@router.post('/{case_id}/override', response_model=CaseResponse)
def override_score(case_id: int, payload: ScoreOverrideRequest, db: Session = Depends(get_db),
                   principal: Principal = Depends(require_roles('project_manager', 'developer', 'executive'))):
    case = _case_for_tenant(db, case_id, principal.tenant_id)
    if not case:
        raise HTTPException(404, 'Case not found')
    if not case.analysis:
        raise HTTPException(400, 'Case must be analyzed before overriding scores')
    
    options = case.analysis.get('options') or []
    target_opt = next((o for o in options if str(o.get('id')) == str(payload.option_id)), None)
    if not target_opt:
        raise HTTPException(404, f"Option '{payload.option_id}' not found in case analysis")
    
    criteria = case.scoring_criteria or []
    target_crit = next((c for c in criteria if c.get('key') == payload.criterion_key), None)
    if not target_crit:
        raise HTTPException(404, f"Criterion '{payload.criterion_key}' not found in scoring criteria")
    
    now_iso = datetime.now(timezone.utc).isoformat()
    prev_raw = (target_opt.get('criterion_scores') or {}).get(payload.criterion_key)
    override_entry = {
        'option_id': payload.option_id,
        'criterion_key': payload.criterion_key,
        'criterion_name': target_crit.get('name', payload.criterion_key),
        'previous_score': prev_raw,
        'new_score': payload.new_score,
        'reason': payload.reason,
        'actor': principal.subject,
        'timestamp': now_iso,
    }
    
    existing_overrides = list(case.override_history or [])
    existing_overrides = [o for o in existing_overrides if not (str(o.get('option_id')) == str(payload.option_id) and o.get('criterion_key') == payload.criterion_key)]
    existing_overrides.append(override_entry)
    case.override_history = existing_overrides
    
    base_options = case.options or [
        {'id': o.get('id'), 'title': o.get('title'), 'description': o.get('description'), 'benefits': o.get('benefits'), 'risks': o.get('risks'), 'conditions': o.get('conditions'), 'criterion_scores': o.get('criterion_scores', {})}
        for o in options
    ]
    recalculated_options = score_options(base_options, criteria=criteria, overrides=existing_overrides)
    
    provenance_map = dict(case.score_provenance or {})
    for opt in recalculated_options:
        opt_id = opt.get('id')
        for prov_key, cell_prov in (opt.get('criterion_provenance') or {}).items():
            provenance_map[f"{opt_id}:{prov_key}"] = cell_prov
            
    case.score_provenance = provenance_map
    case.options = recalculated_options
    
    new_sensitivity = sensitivity_analysis(recalculated_options, criteria)
    
    prev_leader = (case.analysis.get('executive') or {}).get('recommended_option_id')
    new_leader = recalculated_options[0].get('id') if (recalculated_options and recalculated_options[0].get('score_valid') and not recalculated_options[0].get('is_disqualified')) else prev_leader
    leader_changed = (prev_leader != new_leader)
    
    evidence_sources = case.analysis.get('evidence_sources') or []
    facts = case.analysis.get('facts') or []
    unknowns = case.analysis.get('unknowns') or []
    det_conf, conf_breakdown = compose_confidence(
        {'facts': facts, 'missing_information': unknowns, 'sources': evidence_sources},
        recalculated_options,
        clarifications=unknowns,
        sensitivity=new_sensitivity,
    )
    
    from sqlalchemy.orm.attributes import flag_modified
    
    updated_analysis = dict(case.analysis or {})
    exec_block = dict(updated_analysis.get('executive') or {})
    exec_block['recommended_option_id'] = new_leader
    exec_block['confidence'] = det_conf
    exec_block['confidence_breakdown'] = conf_breakdown
    
    if leader_changed:
        exec_block['recommendation_stale'] = True
        exec_block['stale_reason'] = f"تم تعديل الدرجة بواسطة {principal.subject} مما غيّر التوصية من الخيار '{prev_leader}' إلى الخيار '{new_leader}'."
        if case.status == 'approved' and case.approved_option != new_leader:
            case.status = 'recommendation_ready'
            case.approved_option = None

    updated_analysis['executive'] = exec_block
    updated_analysis['options'] = recalculated_options
    updated_analysis['score_provenance'] = provenance_map
    updated_analysis['sensitivity'] = new_sensitivity
    updated_analysis['scenarios'] = new_sensitivity.get('presets', [])
    
    case.analysis = updated_analysis
    case.options = recalculated_options
    case.score_provenance = provenance_map
    case.override_history = existing_overrides
    
    flag_modified(case, 'analysis')
    flag_modified(case, 'options')
    flag_modified(case, 'score_provenance')
    flag_modified(case, 'override_history')
            
    db.commit()
    db.refresh(case)
    
    record_audit(principal.tenant_id, principal.subject, 'score_overridden', auth_type=principal.auth_type,
                 resource_type='case', resource_id=case.id,
                 metadata={'option_id': payload.option_id, 'criterion_key': payload.criterion_key, 'new_score': payload.new_score, 'reason': payload.reason})
    return case


@router.get('/{case_id}/provenance/{option_id}/{criterion_key}')
def get_score_provenance(case_id: int, option_id: str, criterion_key: str, db: Session = Depends(get_db),
                         principal: Principal = Depends(require_principal)):
    case = _case_for_tenant(db, case_id, principal.tenant_id)
    if not case or not case.analysis:
        raise HTTPException(404, 'Analyzed case not found')
    prov_map = case.score_provenance or case.analysis.get('score_provenance') or {}
    cell_key = f"{option_id}:{criterion_key}"
    if cell_key in prov_map:
        return prov_map[cell_key]
    options = case.analysis.get('options') or []
    target_opt = next((o for o in options if str(o.get('id')) == str(option_id)), None)
    if target_opt:
        prov = (target_opt.get('criterion_provenance') or {}).get(criterion_key)
        if prov:
            return prov
    raise HTTPException(404, f"Provenance for option '{option_id}' criterion '{criterion_key}' not found")



@router.post('/{case_id}/approve', response_model=CaseResponse)
def approve(case_id: int, p: ApprovalRequest, db: Session = Depends(get_db), principal: Principal = Depends(require_roles('executive'))):
    x = _case_for_tenant(db, case_id, principal.tenant_id)
    if not x or not x.analysis:
        raise HTTPException(404, 'Analyzed case not found')
    if p.option_id not in {o.get('id') for o in x.analysis.get('options', [])}:
        raise HTTPException(400, 'Invalid option')
    if x.status not in {'recommendation_ready','pending_approval'}: raise HTTPException(409,'Case is not ready for approval')
    x.approved_option=p.option_id; x.decision_owner=p.decision_owner; x.due_date=p.due_date; x.status='approved'
    db.add(DecisionApproval(
        tenant_id=principal.tenant_id,
        case_id=x.id,
        option_id=p.option_id,
        decision_owner=p.decision_owner,
        approved_by=principal.subject,
        status='approved',
    ))
    for index, title in enumerate((x.analysis or {}).get('executive', {}).get('next_actions', [])):
        if not isinstance(title, str) or not title.strip():
            continue
        reference = f'chief_advisor:{index}'
        existing = db.scalar(select(DecisionAction).where(
            DecisionAction.tenant_id == principal.tenant_id,
            DecisionAction.case_id == x.id,
            DecisionAction.source_reference == reference,
        ))
        if not existing:
            db.add(DecisionAction(
                tenant_id=principal.tenant_id,
                case_id=x.id,
                title=title.strip(),
                owner=p.decision_owner,
                due_date=p.due_date,
                created_by=principal.subject,
                source_reference=reference,
            ))
    db.commit(); db.refresh(x)
    record_audit(principal.tenant_id, principal.subject, 'case_approved', auth_type=principal.auth_type,
                 resource_type='case', resource_id=x.id,
                 metadata={'option_id': p.option_id, 'decision_owner': p.decision_owner})
    return x

@router.post('/{case_id}/sensitivity')
def sensitivity(case_id:int,payload:SensitivityRequest,db:Session=Depends(get_db),principal:Principal=Depends(require_principal)):
    case=_case_for_tenant(db,case_id,principal.tenant_id)
    if not case or not case.analysis: raise HTTPException(404,'Analyzed case not found')
    options=case.analysis.get('options') or []
    criteria=case.scoring_criteria or [x for x in (options[0].get('criterion_details') if options else [])]
    result=sensitivity_analysis(options,criteria,dict(payload.weight_changes),dict(payload.score_changes))
    record_audit(principal.tenant_id,principal.subject,'sensitivity_run',auth_type=principal.auth_type,resource_type='case',resource_id=case.id,metadata={'stability':result['stability']})
    return result

def _action_dict(x):
    return {c.name:getattr(x,c.name) for c in x.__table__.columns}

@router.get('/{case_id}/actions')
def list_actions(case_id:int,status:str|None=None,db:Session=Depends(get_db),principal:Principal=Depends(require_principal)):
    if not _case_for_tenant(db,case_id,principal.tenant_id):raise HTTPException(404,'Case not found')
    q=select(DecisionAction).where(DecisionAction.case_id==case_id,DecisionAction.tenant_id==principal.tenant_id)
    if status:q=q.where(DecisionAction.status==status)
    return [_action_dict(x) for x in db.scalars(q.order_by(DecisionAction.created_at.desc())).all()]

@router.post('/{case_id}/actions',status_code=201)
def create_action(case_id:int,payload:ActionCreate,db:Session=Depends(get_db),principal:Principal=Depends(require_roles('project_manager','executive'))):
    case=_case_for_tenant(db,case_id,principal.tenant_id)
    if not case:raise HTTPException(404,'Case not found')
    if payload.status not in {'not_started','in_progress','blocked','completed','cancelled'}:raise HTTPException(422,'Invalid action status')
    if payload.dependency_id and not db.scalar(select(DecisionAction).where(DecisionAction.id==payload.dependency_id,DecisionAction.case_id==case_id,DecisionAction.tenant_id==principal.tenant_id)):raise HTTPException(404,'Dependency not found')
    action=DecisionAction(tenant_id=principal.tenant_id,case_id=case_id,created_by=principal.subject,**payload.model_dump())
    if action.status=='completed':action.completion_date=date.today()
    db.add(action);db.commit();db.refresh(action)
    record_audit(principal.tenant_id,principal.subject,'action_created',auth_type=principal.auth_type,resource_type='decision_action',resource_id=action.id,metadata={'case_id':case_id})
    return _action_dict(action)

@router.patch('/{case_id}/actions/{action_id}')
def update_action(case_id:int,action_id:int,payload:ActionUpdate,db:Session=Depends(get_db),principal:Principal=Depends(require_roles('project_manager','executive'))):
    action=db.scalar(select(DecisionAction).where(DecisionAction.id==action_id,DecisionAction.case_id==case_id,DecisionAction.tenant_id==principal.tenant_id))
    if not action:raise HTTPException(404,'Action not found')
    values=payload.model_dump(exclude_unset=True)
    if values.get('status') and values['status'] not in {'not_started','in_progress','blocked','completed','cancelled'}:raise HTTPException(422,'Invalid action status')
    for key,value in values.items():setattr(action,key,value)
    if values.get('status')=='completed' and not action.completion_date:action.completion_date=date.today()
    if values.get('status')!='completed' and 'status' in values:action.completion_date=None
    db.commit();db.refresh(action)
    record_audit(principal.tenant_id,principal.subject,'action_updated',auth_type=principal.auth_type,resource_type='decision_action',resource_id=action.id,metadata={'fields':sorted(values)})
    return _action_dict(action)

@router.get('/{case_id}/outcomes')
def outcomes(case_id:int,db:Session=Depends(get_db),principal:Principal=Depends(require_principal)):
    if not _case_for_tenant(db,case_id,principal.tenant_id):raise HTTPException(404,'Case not found')
    return [_action_dict(x) for x in db.scalars(select(DecisionOutcome).where(DecisionOutcome.case_id==case_id,DecisionOutcome.tenant_id==principal.tenant_id).order_by(DecisionOutcome.created_at.desc())).all()]

@router.post('/{case_id}/outcomes',status_code=201)
def record_outcome(case_id:int,payload:OutcomeCreate,db:Session=Depends(get_db),principal:Principal=Depends(require_roles('project_manager','executive'))):
    case=_case_for_tenant(db,case_id,principal.tenant_id)
    if not case or case.status not in {'approved','archived'}:raise HTTPException(409,'Outcome requires an approved decision')
    if payload.result not in {'success','partial','failure'}:raise HTTPException(422,'Invalid outcome result')
    outcome=DecisionOutcome(tenant_id=principal.tenant_id,case_id=case_id,recorded_by=principal.subject,**payload.model_dump())
    db.add(outcome);db.commit();db.refresh(outcome)
    record_audit(principal.tenant_id,principal.subject,'outcome_recorded',auth_type=principal.auth_type,resource_type='decision_outcome',resource_id=outcome.id,metadata={'case_id':case_id,'result':outcome.result})
    return _action_dict(outcome)
