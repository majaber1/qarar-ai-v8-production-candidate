from __future__ import annotations
from sqlalchemy import select
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from app.core.audit import record_audit
from app.core.auth import current_principal
from app.core.mcp_auth import MCPAuthMiddleware
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.ratelimit import check_ai_rate_limit, check_budget
from app.models.case import DecisionCase
from app.models.security import DecisionApproval
from app.schemas.case import CaseCreate
from app.services.knowledge_qa import ask_knowledge
from app.services.fabric import hybrid_search, ingest_source
from app.services.object_storage import storage
from app.services.advisor import analyze_case
from app.services.automation import execute as execute_automation

mcp=MCPServer('Qarar AI V8')

def _require_mcp_roles(*roles):
    p=current_principal()
    # The dedicated service identity may operate MCP tools, but it can never satisfy the
    # executive-only human approval gate.
    if 'integration_service' in p.roles and roles != ('executive',):
        return p
    if not p.has_any_role(roles):
        raise PermissionError('Insufficient MCP role')
    return p

def _case_for_tenant(db,case_id,tenant_id):
    return db.scalar(select(DecisionCase).where(DecisionCase.id==case_id,DecisionCase.tenant_id==tenant_id))

@mcp.tool()
def health()->dict:
    """Check authenticated Qarar MCP health."""
    p=current_principal()
    return {'status':'ok','product':'Qarar AI V8','tenant_id':p.tenant_id,'subject':p.subject,'capabilities':['knowledge','decisions','automation']}

@mcp.tool()
def ask_qarar(question:str,case_id:int|None=None,language:str='ar',research_mode:str='official_plus_organization')->dict:
    """Ask Qarar using tenant-scoped organization evidence plus optional official/public research."""
    p=_require_mcp_roles('executive','project_manager','analyst','developer')
    return ask_knowledge(question,case_id=case_id,language=language,mode=research_mode,tenant_id=p.tenant_id)

@mcp.tool()
def search_evidence(query:str,case_id:int|None=None,limit:int=10)->dict:
    """Search tenant-scoped Knowledge Fabric evidence chunks with citation metadata, without invoking the LLM."""
    p=_require_mcp_roles('executive','project_manager','analyst','developer')
    results=hybrid_search(query,case_id=case_id,tenant_id=p.tenant_id,limit=min(max(limit,1),30))
    return {'query':query,'results':results}

@mcp.tool()
def add_evidence(case_id:int,title:str,text:str,trust_level:str='B')->dict:
    """Add a text evidence note to a tenant-scoped case. Ordinary evidence cannot self-assert Trust A."""
    p=_require_mcp_roles('project_manager','developer')
    db=SessionLocal()
    try:
        case=_case_for_tenant(db,case_id,p.tenant_id)
        if not case:return {'error':'case not found'}
        from app.models.fabric import KnowledgeSource
        effective_trust=trust_level if trust_level in {'B','C','D'} else 'B'
        key=storage().put(f"{title}.txt",text.encode('utf-8'))
        src=KnowledgeSource(tenant_id=p.tenant_id,case_id=case_id,source_type='mcp_note',title=title,
                             source_ref='mcp:add_evidence',object_key=key,trust_level=effective_trust,status='queued')
        db.add(src);db.commit();db.refresh(src)
        ingest_source(src.id)
        record_audit(p.tenant_id,p.subject,'evidence_added_via_mcp',auth_type='mcp',resource_type='knowledge_source',resource_id=src.id)
        return {'id':src.id,'title':src.title,'trust_level':src.trust_level,'status':'ready'}
    finally:db.close()

@mcp.tool()
def create_case(title:str,description:str,urgency:str='medium',category:str|None=None,language:str='ar')->dict:
    """Create a new tenant-scoped decision case."""
    p=_require_mcp_roles('project_manager','developer')
    db=SessionLocal()
    try:
        x=DecisionCase(tenant_id=p.tenant_id,created_by=p.subject,title=title,description=description,
                        urgency=urgency,category=category,language=language)
        db.add(x);db.commit();db.refresh(x)
        record_audit(p.tenant_id,p.subject,'case_created_via_mcp',auth_type='mcp',resource_type='case',resource_id=x.id)
        return {'id':x.id,'title':x.title,'status':x.status}
    finally:db.close()

@mcp.tool()
def get_case(case_id:int)->dict:
    """Get a tenant-scoped decision case and its latest decision summary."""
    p=_require_mcp_roles('executive','project_manager','analyst','developer')
    db=SessionLocal()
    try:
        x=_case_for_tenant(db,case_id,p.tenant_id)
        if not x:return {'error':'case not found'}
        return {'id':x.id,'title':x.title,'description':x.description,'status':x.status,'analysis_source':x.analysis_source,'analysis':x.analysis}
    finally:db.close()

@mcp.tool()
def list_cases(status:str|None=None,limit:int=20)->dict:
    """List tenant-scoped decision cases, optionally filtered by status."""
    p=_require_mcp_roles('executive','project_manager','analyst','developer')
    db=SessionLocal()
    try:
        stmt=select(DecisionCase).where(DecisionCase.tenant_id==p.tenant_id)
        if status:stmt=stmt.where(DecisionCase.status==status)
        stmt=stmt.order_by(DecisionCase.created_at.desc()).limit(min(max(limit,1),100))
        rows=db.scalars(stmt).all()
        return {'cases':[{'id':x.id,'title':x.title,'status':x.status,'urgency':x.urgency,'category':x.category} for x in rows]}
    finally:db.close()

@mcp.tool()
def get_case_status(case_id:int)->dict:
    """Get the lifecycle status of a tenant-scoped case (open/recommendation_ready/approved)."""
    p=_require_mcp_roles('executive','project_manager','analyst','developer')
    db=SessionLocal()
    try:
        x=_case_for_tenant(db,case_id,p.tenant_id)
        if not x:return {'error':'case not found'}
        return {'id':x.id,'status':x.status,'approved_option':x.approved_option,'decision_owner':x.decision_owner}
    finally:db.close()

@mcp.tool()
def get_executive_brief(case_id:int)->dict:
    """Get the executive-facing decision brief only: recommendation, confidence, why, risks, next actions."""
    p=_require_mcp_roles('executive','project_manager','developer')
    db=SessionLocal()
    try:
        x=_case_for_tenant(db,case_id,p.tenant_id)
        if not x or not x.analysis:return {'error':'no recommendation yet for this case'}
        return x.analysis.get('executive',{})
    finally:db.close()

@mcp.tool()
def get_decision(case_id:int)->dict:
    """Get the full decision record: options, scoring, critic challenge and chief advisor recommendation."""
    p=_require_mcp_roles('executive','project_manager','developer')
    db=SessionLocal()
    try:
        x=_case_for_tenant(db,case_id,p.tenant_id)
        if not x or not x.analysis:return {'error':'no recommendation yet for this case'}
        return {'options':x.analysis.get('options',[]),'critic':x.analysis.get('critic',{}),
                'executive':x.analysis.get('executive',{}),'status':x.status}
    finally:db.close()

@mcp.tool()
def get_risks(case_id:int)->dict:
    """Get the top risks identified for a tenant-scoped case."""
    p=_require_mcp_roles('executive','project_manager','analyst','developer')
    db=SessionLocal()
    try:
        x=_case_for_tenant(db,case_id,p.tenant_id)
        if not x or not x.analysis:return {'error':'no recommendation yet for this case'}
        return {'top_risks':x.analysis.get('executive',{}).get('top_risks',[])}
    finally:db.close()

@mcp.tool()
def run_decision_council(case_id:int)->dict:
    """Run Qarar decision council for a tenant-scoped existing case."""
    p=_require_mcp_roles('project_manager','developer')
    ok,reason=check_budget(p.tenant_id)
    if not ok:raise PermissionError(reason)
    ok,reason=check_ai_rate_limit(p.subject)
    if not ok:raise PermissionError(reason)
    db=SessionLocal()
    try:
        x=_case_for_tenant(db,case_id,p.tenant_id)
        if not x:return {'error':'case not found'}
        r=analyze_case(x.id,x.title,x.description,x.urgency,x.category,x.language,p.tenant_id)
        x.selected_agents=r['selected_agents'];x.skipped_agents=r['skipped_agents'];x.agent_results=r['agent_results'];x.analysis=r['analysis'];x.audit_log=r['audit_log'];x.analysis_source=r['analysis_source'];x.status='recommendation_ready';db.commit()
        record_audit(p.tenant_id,p.subject,'case_analyzed_via_mcp',auth_type='mcp',resource_type='case',resource_id=x.id)
        return {'case_id':x.id,'status':x.status,'analysis_source':x.analysis_source,'executive':x.analysis.get('executive') if x.analysis else None}
    finally:db.close()

@mcp.tool()
def approve_decision(case_id:int,option_id:str,decision_owner:str)->dict:
    """Approve a decision option for a tenant-scoped case. Requires the executive role; persists a
    server-verified DecisionApproval record — the same one the REST /approve endpoint writes, so
    automation approval enforcement is identical regardless of which channel approved the case."""
    p=_require_mcp_roles('executive')
    db=SessionLocal()
    try:
        x=_case_for_tenant(db,case_id,p.tenant_id)
        if not x or not x.analysis:return {'error':'analyzed case not found'}
        if option_id not in {o.get('id') for o in x.analysis.get('options',[])}:
            return {'error':'invalid option_id'}
        x.approved_option=option_id;x.decision_owner=decision_owner;x.status='approved'
        db.add(DecisionApproval(tenant_id=p.tenant_id,case_id=x.id,option_id=option_id,
                                 decision_owner=decision_owner,approved_by=p.subject,status='approved'))
        db.commit()
        record_audit(p.tenant_id,p.subject,'case_approved_via_mcp',auth_type='mcp',resource_type='case',resource_id=x.id)
        return {'case_id':x.id,'status':x.status,'approved_option':x.approved_option}
    finally:db.close()

@mcp.tool()
def execute_approved_workflow(workflow_id:str,case_id:int,payload:dict,dry_run:bool=True)->dict:
    """Execute or dry-run a Qarar workflow. Non-dry-run execution requires a server-verified approval record."""
    p=_require_mcp_roles('executive','project_manager')
    payload={**payload,'case_id':case_id}
    result=execute_automation(workflow_id,payload,dry_run=dry_run,tenant_id=p.tenant_id,actor=p.subject)
    record_audit(p.tenant_id,p.subject,'automation_run_via_mcp',auth_type='mcp',resource_type='case',resource_id=case_id,
                 metadata={'workflow_id':workflow_id,'dry_run':dry_run,'status':result.get('status')})
    return result


security=TransportSecuritySettings(allowed_hosts=settings.mcp_host_list, allowed_origins=settings.mcp_origin_list)
_mcp_app=mcp.streamable_http_app(transport_security=security)
app=MCPAuthMiddleware(_mcp_app)
