from __future__ import annotations
import asyncio, json, os
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.platform import MCPServerRegistration

# --- System-level catalog (config/mcp_servers.json). Read-only, available to every tenant. ---

def _system_servers() -> list[dict]:
    p = Path(settings.mcp_servers_file)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding='utf-8')).get('servers', [])
    except Exception:
        return []


def _system_headers(s: dict) -> dict:
    auth = s.get('auth') or {}
    env = auth.get('env')
    token = os.environ.get(env, '') if env else ''
    return {'Authorization': f'Bearer {token}'} if token else {}


# --- Tenant-owned registry (DB). Registered/edited/disabled through the Connect API. ---

def register_server(tenant_id: str, name: str, url: str, *, auth_type: str = 'none',
                     auth_env_var: str | None = None, tool_allowlist: list[str] | None = None,
                     timeout_seconds: float | None = None, created_by: str = 'unknown') -> MCPServerRegistration:
    server_key = name.strip().lower().replace(' ', '-')[:80] or 'server'
    with SessionLocal() as db:
        row = MCPServerRegistration(
            tenant_id=tenant_id, server_key=server_key, name=name, url=url, enabled=True,
            auth_type=auth_type, auth_env_var=auth_env_var,
            tool_allowlist_json=json.dumps(tool_allowlist) if tool_allowlist else None,
            timeout_seconds=timeout_seconds or settings.mcp_gateway_timeout_seconds,
            created_by=created_by,
        )
        db.add(row); db.commit(); db.refresh(row)
        return row


def list_registrations(tenant_id: str) -> list[MCPServerRegistration]:
    with SessionLocal() as db:
        return list(db.scalars(select(MCPServerRegistration).where(MCPServerRegistration.tenant_id == tenant_id)).all())


def set_registration_enabled(tenant_id: str, reg_id: int, enabled: bool) -> MCPServerRegistration | None:
    with SessionLocal() as db:
        row = db.scalar(select(MCPServerRegistration).where(
            MCPServerRegistration.id == reg_id, MCPServerRegistration.tenant_id == tenant_id))
        if not row:
            return None
        row.enabled = enabled
        db.commit(); db.refresh(row)
        return row


def delete_registration(tenant_id: str, reg_id: int) -> bool:
    with SessionLocal() as db:
        row = db.scalar(select(MCPServerRegistration).where(
            MCPServerRegistration.id == reg_id, MCPServerRegistration.tenant_id == tenant_id))
        if not row:
            return False
        db.delete(row); db.commit()
        return True


def _registration_dict(row: MCPServerRegistration) -> dict:
    return {
        'id': row.id, 'server_key': row.server_key, 'name': row.name, 'url': row.url, 'enabled': row.enabled,
        'auth_type': row.auth_type, 'scope': 'tenant', 'timeout_seconds': row.timeout_seconds,
        'tool_allowlist': json.loads(row.tool_allowlist_json) if row.tool_allowlist_json else None,
        'last_health_status': row.last_health_status,
        'last_health_at': row.last_health_at.isoformat() if row.last_health_at else None,
    }


def server_catalog(tenant_id: str = 'default') -> list[dict]:
    system = [{**{k: v for k, v in s.items() if k != 'auth'}, 'scope': 'system'} for s in _system_servers()]
    tenant = [_registration_dict(r) for r in list_registrations(tenant_id)]
    return system + tenant


def _find(server_id: str, tenant_id: str) -> tuple[dict | None, str | None]:
    """Returns (server_config, source) where source is 'system' or 'tenant'."""
    for s in _system_servers():
        if s.get('id') == server_id:
            return s, 'system'
    with SessionLocal() as db:
        row = db.scalar(select(MCPServerRegistration).where(
            MCPServerRegistration.tenant_id == tenant_id,
            (MCPServerRegistration.server_key == server_id) | (MCPServerRegistration.id == _safe_int(server_id)),
        ))
        if row:
            return {
                'id': row.server_key, 'url': row.url, 'enabled': row.enabled,
                'auth': {'type': 'bearer', 'env': row.auth_env_var} if row.auth_type == 'bearer_env' else {},
                'tool_allowlist': json.loads(row.tool_allowlist_json) if row.tool_allowlist_json else None,
                'timeout_seconds': row.timeout_seconds, '_row_id': row.id,
            }, 'tenant'
    return None, None


def _safe_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return -1


def _headers_for(s: dict) -> dict:
    return _system_headers(s)


async def _with_session(server_id: str, tenant_id: str, action: str, tool: str | None = None, args: dict | None = None):
    s, source = _find(server_id, tenant_id)
    if not s or not s.get('enabled'):
        raise ValueError('MCP server not found or disabled')

    allowlist = s.get('tool_allowlist')
    if action == 'call' and allowlist and tool not in allowlist:
        raise PermissionError(f"Tool '{tool}' is not in the allowlist for this server")

    import httpx
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    timeout = float(s.get('timeout_seconds') or settings.mcp_gateway_timeout_seconds)
    # FIX (V5.1 regression): the installed MCP SDK's streamable_http_client() does not accept a
    # `headers=` kwarg. Authentication/timeouts are configured on an httpx.AsyncClient and
    # passed as `http_client=` instead. See mcp.client.streamable_http.streamable_http_client docstring.
    http_client = httpx.AsyncClient(headers=_headers_for(s), timeout=timeout,follow_redirects=False)
    try:
        async with streamable_http_client(s['url'], http_client=http_client) as streams:
            read, write = streams[0], streams[1]
            async with ClientSession(read, write) as session:
                await session.initialize()
                if action == 'tools':
                    r = await session.list_tools()
                    tools = [{'name': t.name, 'description': t.description, 'inputSchema': getattr(t, 'inputSchema', {})} for t in r.tools]
                    if allowlist:
                        tools = [t for t in tools if t['name'] in allowlist]
                    return tools
                r = await session.call_tool(tool, arguments=args or {})
                return {
                    'content': [getattr(x, 'text', str(x)) for x in r.content],
                    'is_error': getattr(r, 'is_error', getattr(r, 'isError', False)),
                    'structuredContent': getattr(r, 'structuredContent', None),
                }
    finally:
        await http_client.aclose()


def list_tools(server_id: str, tenant_id: str = 'default'):
    return asyncio.run(_with_session(server_id, tenant_id, 'tools'))


def call_tool(server_id: str, tool: str, args: dict, tenant_id: str = 'default'):
    return asyncio.run(_with_session(server_id, tenant_id, 'call', tool, args))


def health_test(server_id: str, tenant_id: str = 'default') -> dict:
    """Attempt list_tools with the server's configured timeout; persist status for tenant-owned servers."""
    s, source = _find(server_id, tenant_id)
    if not s:
        return {'status': 'not_found'}
    try:
        tools = asyncio.run(_with_session(server_id, tenant_id, 'tools'))
        result = {'status': 'ok', 'tool_count': len(tools), 'checked_at': datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        result = {'status': 'error', 'detail': str(e), 'checked_at': datetime.now(timezone.utc).isoformat()}

    if source == 'tenant':
        with SessionLocal() as db:
            row = db.get(MCPServerRegistration, s['_row_id'])
            if row:
                row.last_health_status = result['status']
                row.last_health_at = datetime.now(timezone.utc)
                row.last_health_detail = result.get('detail') or f"{result.get('tool_count', 0)} tools"
                db.commit()
    return result
