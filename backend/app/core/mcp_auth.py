from starlette.responses import JSONResponse
from app.core.auth import authenticate_key, authenticate_oidc, reset_current_principal, set_current_principal

class MCPAuthMiddleware:
    """Authenticate every MCP Streamable HTTP request before protocol dispatch."""
    def __init__(self, app): self.app=app

    async def __call__(self, scope, receive, send):
        if scope.get('type') != 'http':
            await self.app(scope, receive, send); return
        headers={k.decode('latin-1').lower():v.decode('latin-1') for k,v in scope.get('headers',[])}
        key=headers.get('x-qarar-api-key')
        bearer=None
        if not key:
            auth=headers.get('authorization','')
            if auth.lower().startswith('bearer '): bearer=key=auth.split(' ',1)[1].strip()
        principal=authenticate_key(key)
        if not principal and bearer:
            principal=authenticate_oidc(bearer)
        if not principal:
            response=JSONResponse({'detail':'Authentication required'},status_code=401)
            await response(scope,receive,send); return
        token=set_current_principal(principal)
        try: await self.app(scope,receive,send)
        finally: reset_current_principal(token)
