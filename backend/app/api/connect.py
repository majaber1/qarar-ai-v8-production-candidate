from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Literal
from app.core.audit import record_audit
from app.core.auth import Principal, require_principal, require_roles
from app.core.config import settings
from app.services.connectors import catalog
from app.services import mcp_gateway
from app.services.automation import apply_callback, catalog as automation_catalog, execute
from app.services.callback_security import verify_callback

router = APIRouter(prefix='/connect', tags=['connect'])


class ToolCall(BaseModel):
    tool: str
    arguments: dict = Field(default_factory=dict)


class AutoRun(BaseModel):
    workflow_id: str
    case_id: int | None = None
    payload: dict = Field(default_factory=dict)
    dry_run: bool = True


class RegisterServer(BaseModel):
    name: str
    url: str
    auth_type: str = 'none'  # 'none' | 'bearer_env'
    auth_env_var: str | None = None
    tool_allowlist: list[str] | None = None
    timeout_seconds: float | None = None


class AutomationCallback(BaseModel):
    status: Literal['executed','failed','cancelled']
    detail: dict = Field(default_factory=dict)


@router.get('/catalog')
def get_catalog(principal: Principal = Depends(require_principal)):
    return {'connectors': catalog(), 'mcp_servers': mcp_gateway.server_catalog(principal.tenant_id), 'automations': automation_catalog()}


@router.get('/mcp/servers')
def list_servers(principal: Principal = Depends(require_roles('developer', 'admin'))):
    return mcp_gateway.server_catalog(principal.tenant_id)


@router.post('/mcp/servers')
def register(req: RegisterServer, principal: Principal = Depends(require_roles('developer', 'admin'))):
    row = mcp_gateway.register_server(
        principal.tenant_id, req.name, req.url, auth_type=req.auth_type, auth_env_var=req.auth_env_var,
        tool_allowlist=req.tool_allowlist, timeout_seconds=req.timeout_seconds, created_by=principal.subject,
    )
    record_audit(principal.tenant_id, principal.subject, 'mcp_server_registered', auth_type=principal.auth_type,
                 resource_type='mcp_server', resource_id=row.id, metadata={'name': req.name, 'url': req.url})
    return {'id': row.id, 'server_key': row.server_key, 'name': row.name}


@router.patch('/mcp/servers/{reg_id}')
def set_enabled(reg_id: int, enabled: bool, principal: Principal = Depends(require_roles('developer', 'admin'))):
    row = mcp_gateway.set_registration_enabled(principal.tenant_id, reg_id, enabled)
    if not row:
        raise HTTPException(404, 'MCP server registration not found')
    record_audit(principal.tenant_id, principal.subject, 'mcp_server_toggled', auth_type=principal.auth_type,
                 resource_type='mcp_server', resource_id=reg_id, metadata={'enabled': enabled})
    return {'id': row.id, 'enabled': row.enabled}


@router.delete('/mcp/servers/{reg_id}')
def delete_server(reg_id: int, principal: Principal = Depends(require_roles('developer', 'admin'))):
    ok = mcp_gateway.delete_registration(principal.tenant_id, reg_id)
    if not ok:
        raise HTTPException(404, 'MCP server registration not found')
    record_audit(principal.tenant_id, principal.subject, 'mcp_server_deleted', auth_type=principal.auth_type,
                 resource_type='mcp_server', resource_id=reg_id)
    return {'status': 'deleted'}


@router.post('/mcp/{server_id}/health')
def health(server_id: str, principal: Principal = Depends(require_roles('developer', 'admin'))):
    return mcp_gateway.health_test(server_id, principal.tenant_id)


@router.get('/mcp/{server_id}/tools')
def tools(server_id: str, principal: Principal = Depends(require_roles('developer', 'admin'))):
    try:
        return {'server_id': server_id, 'tools': mcp_gateway.list_tools(server_id, principal.tenant_id)}
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post('/mcp/{server_id}/call')
def call(server_id: str, req: ToolCall, principal: Principal = Depends(require_roles('developer', 'admin'))):
    try:
        result = mcp_gateway.call_tool(server_id, req.tool, req.arguments, principal.tenant_id)
        record_audit(principal.tenant_id, principal.subject, 'mcp_gateway_tool_call', auth_type=principal.auth_type,
                     resource_type='mcp_server', resource_id=server_id, metadata={'tool': req.tool})
        return result
    except PermissionError as e:
        raise HTTPException(403, str(e))
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post('/automation/run')
def run(req: AutoRun, principal: Principal = Depends(require_roles('project_manager', 'executive'))):
    try:
        result = execute(req.workflow_id, {**req.payload, 'case_id': req.case_id}, dry_run=req.dry_run,
                          tenant_id=principal.tenant_id, actor=principal.subject)
        record_audit(principal.tenant_id, principal.subject, 'automation_run', auth_type=principal.auth_type,
                     resource_type='case', resource_id=req.case_id,
                     metadata={'workflow_id': req.workflow_id, 'dry_run': req.dry_run, 'status': result.get('status')})
        return result
    except PermissionError as e:
        raise HTTPException(403, str(e))
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post('/automation/callback/{run_id}')
async def automation_callback(run_id: int, request: Request,
                              x_qarar_timestamp: str | None = Header(default=None),
                              x_qarar_nonce: str | None = Header(default=None),
                              x_qarar_signature: str | None = Header(default=None)):
    body = await request.body()
    try:
        verify_callback(run_id, body, x_qarar_timestamp, x_qarar_nonce, x_qarar_signature)
        req = AutomationCallback.model_validate_json(body)
        result = apply_callback(run_id, req.status, req.detail)
        record_audit(result['tenant_id'], 'n8n-callback', 'automation_callback', auth_type='webhook_hmac',
                     resource_type='automation_run', resource_id=run_id, metadata={'status': req.status})
        return result
    except PermissionError as e:
        raise HTTPException(401, str(e))
