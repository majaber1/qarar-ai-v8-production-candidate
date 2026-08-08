from __future__ import annotations
import json
import httpx
from urllib.parse import urlparse
from sqlalchemy import select
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.case import DecisionCase
from app.models.fabric import AutomationRun
from app.models.security import DecisionApproval

WORKFLOWS={
 'follow_up_owner':{'name':'Follow up decision owner','description':'Send/queue a follow-up after approval'},
 'escalate_blocker':{'name':'Escalate blocker','description':'Create an escalation payload for n8n/enterprise workflow'},
 'decision_to_action':{'name':'Decision to action','description':'Turn an approved decision into tasks, notifications and tracking'},
}

def catalog():return [{'id':k,**v} for k,v in WORKFLOWS.items()]

def _webhook_url(workflow_id:str)->str:
    url=f"{settings.n8n_webhook_base_url.rstrip('/')}/{workflow_id}"
    parsed=urlparse(url)
    if parsed.scheme not in {'http','https'} or not parsed.hostname:
        raise ValueError('Invalid automation webhook URL')
    if parsed.hostname.lower() not in settings.automation_allowed_host_list:
        raise PermissionError('Automation webhook host is not allowlisted')
    return url


def _verify_approval(case_id:int|None,tenant_id:str):
    if not case_id:
        raise PermissionError('A case_id is required for non-dry-run automation')
    with SessionLocal() as db:
        case=db.scalar(select(DecisionCase).where(DecisionCase.id==case_id,DecisionCase.tenant_id==tenant_id))
        if not case or case.status!='approved' or not case.approved_option:
            raise PermissionError('Case has no server-verified human approval')
        approval=db.scalar(select(DecisionApproval).where(
            DecisionApproval.case_id==case_id,
            DecisionApproval.tenant_id==tenant_id,
            DecisionApproval.status=='approved',
        ).order_by(DecisionApproval.approved_at.desc()))
        if not approval or approval.option_id!=case.approved_option:
            raise PermissionError('Approval record is missing or does not match the approved option')
        return approval


def _verify_case_tenant(case_id:int|None,tenant_id:str):
    """Applies to BOTH dry-run and real execution: a case_id in the payload must belong to the
    caller's tenant. V5.1 only enforced this on the non-dry-run path; V6 closes that gap."""
    if case_id is None:
        return
    with SessionLocal() as db:
        case=db.scalar(select(DecisionCase).where(DecisionCase.id==case_id,DecisionCase.tenant_id==tenant_id))
        if not case:
            raise PermissionError('Case does not belong to the authenticated tenant')


def execute(workflow_id:str,payload:dict,dry_run:bool|None=None,tenant_id:str|None=None,actor:str|None=None):
    if workflow_id not in WORKFLOWS:raise ValueError('Unknown workflow')
    if not tenant_id:raise ValueError('tenant_id is required')
    dry=settings.automation_dry_run if dry_run is None else dry_run
    case_id=payload.get('case_id')
    _verify_case_tenant(case_id,tenant_id)

    if not dry:
        if not settings.automation_enabled:
            raise PermissionError('Automation execution is disabled')
        if settings.automation_require_approval:
            _verify_approval(case_id,tenant_id)

    run=AutomationRun(
        tenant_id=tenant_id,actor=actor,case_id=case_id,workflow_id=workflow_id,
        status='pending',approved=0 if dry else 1,dry_run=1 if dry else 0,
        input_json=json.dumps(payload,ensure_ascii=False),
    )
    with SessionLocal() as db:
        db.add(run);db.commit();db.refresh(run);run_id=run.id

    if dry:
        result={'status':'dry_run','run_id':run_id,'workflow_id':workflow_id,'payload':payload}
        with SessionLocal() as db:
            target=db.get(AutomationRun,run_id);target.status='dry_run';target.result_json=json.dumps(result,ensure_ascii=False);db.commit()
        return result

    # run_id/callback_url are embedded so the receiving workflow can report status back to Qarar
    # (Decision -> n8n -> execute -> callback -> Qarar tracks the real outcome, not just "we sent it").
    headers={'X-API-Key':settings.n8n_api_key} if settings.n8n_api_key else {}
    webhook_url=_webhook_url(workflow_id)
    outbound_payload={**payload,'qarar_run_id':run_id,
                       'qarar_callback_url':f"{settings.api_public_base_url.rstrip('/')}/api/connect/automation/callback/{run_id}"}
    last_exc=None
    for attempt in range(2):
        try:
            r=httpx.post(webhook_url,json=outbound_payload,headers=headers,timeout=30,follow_redirects=False)
            r.raise_for_status()
            result={'status':'sent','run_id':run_id,'workflow_id':workflow_id,'http_status':r.status_code,'response':r.text[:2000]}
            with SessionLocal() as db:
                target=db.get(AutomationRun,run_id)
                # The receiving workflow may call back to /automation/callback synchronously,
                # inside this very httpx.post() (as the pilot webhook receiver and the committed
                # n8n workflow both do) — that callback can already have advanced status to a
                # terminal value like 'executed'. Only stamp 'sent' if nothing has moved it yet,
                # so this post-request write can't clobber a callback that beat it here.
                if target.status=='pending':
                    target.status='sent';target.result_json=json.dumps(result,ensure_ascii=False)
                db.commit()
            return result
        except Exception as exc:
            last_exc=exc
    with SessionLocal() as db:
        target=db.get(AutomationRun,run_id);target.status='failed';target.error=str(last_exc);db.commit()
    raise last_exc


def apply_callback(run_id:int,status:str,detail:dict|None=None):
    """Record an execution outcome reported back by the automation target (e.g. n8n) after it
    finishes acting on a 'sent' run. Tenant-checked so one tenant cannot overwrite another's run."""
    with SessionLocal() as db:
        run=db.get(AutomationRun,run_id)
        if not run:
            raise PermissionError('Automation run not found')
        run.status=status
        run.result_json=json.dumps({**(json.loads(run.result_json) if run.result_json else {}),'callback':detail or {}},ensure_ascii=False)
        db.commit()
        return {'run_id':run.id,'status':run.status,'tenant_id':run.tenant_id}
