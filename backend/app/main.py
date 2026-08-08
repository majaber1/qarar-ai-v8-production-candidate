import json
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.auth import Principal, authenticate_headers,require_principal
from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import configure_logging, log_event
from app.core.ratelimit import check_rate_limit
from app.api.cases import router as cases_router
from app.api.platform import router as platform_router
from app.api.knowledge import router as legacy_knowledge_router
from app.api.fabric import router as fabric_router
from app.api.connect import router as connect_router
from app.models.knowledge import KnowledgeItem
from app.models.fabric import KnowledgeSource, KnowledgeChunk, AutomationRun
from app.models.security import DecisionApproval, AutomationCallbackReceipt
from app.models.platform import AuditEvent, UsageRecord, CostBudget, MCPServerRegistration, ScanResult
from app.services.registry import registry

configure_logging()
if settings.environment.lower() in {'development','dev','test'}:
    Base.metadata.create_all(bind=engine)


def _security_check():
    if settings.environment.lower() not in {'development', 'dev', 'test'}:
        try:
            keys = json.loads(settings.qarar_api_keys_json or '{}')
        except Exception:
            keys = {}
        if not keys and not settings.mcp_api_key and not settings.oidc_enabled:
            raise RuntimeError('Qarar cannot start outside development without configured authentication (API keys or OIDC)')
        if any('change-me' in str(k).lower() for k in keys):
            raise RuntimeError('Development API key detected outside development environment')
        if '*' in settings.cors_list:
            raise RuntimeError('Wildcard CORS is forbidden outside development')
        if settings.automation_enabled and not settings.automation_callback_secret:
            raise RuntimeError('AUTOMATION_CALLBACK_SECRET is required when automation is enabled')


@asynccontextmanager
async def lifespan(app: FastAPI):
    _security_check()
    yield


app = FastAPI(title='Qarar AI V8 — Enterprise Decision Intelligence Platform', version='8.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])


@app.middleware('http')
async def observability_and_rate_limit(request: Request, call_next):
    request_id = request.headers.get('x-request-id') or uuid.uuid4().hex
    request.state.request_id = request_id
    start = time.perf_counter()

    # Use authenticated identity/tenant when available; fall back to IP only for public probes.
    principal=authenticate_headers(request.headers.get('x-qarar-api-key'),request.headers.get('authorization'))
    client_ip=request.client.host if request.client else 'anon'
    user_key=principal.subject if principal else client_ip
    tenant_key=principal.tenant_id if principal else client_ip
    allowed, reason = check_rate_limit(user_key,tenant_key)
    if not allowed:
        log_event('rate_limit_blocked', request_id=request_id, path=request.url.path, reason=reason)
        return JSONResponse({'detail': reason}, status_code=429)

    response = await call_next(request)
    response.headers['X-Request-ID'] = request_id
    duration_ms = int((time.perf_counter() - start) * 1000)
    log_event('http_request', request_id=request_id, method=request.method, path=request.url.path,
              status_code=response.status_code, duration_ms=duration_ms)
    return response


for r in [cases_router, platform_router, legacy_knowledge_router, fabric_router, connect_router]:
    app.include_router(r, prefix='/api')


@app.get('/')
def root():
    return {'name': 'Qarar AI V8', 'category': 'Enterprise Decision Intelligence Platform', 'docs': '/docs',
            'mcp': settings.mcp_public_base_url.rstrip('/') + '/mcp', 'security': 'authenticated tenant-scoped API'}


@app.get('/api/health')
def health():
    return {'status': 'ok', 'version': '8.0.0', 'ai_enabled': settings.ai_enabled, 'provider': settings.ai_provider,
            'database': 'postgresql' if settings.is_postgres else 'sqlite',
            'knowledge': 'ready', 'mcp_gateway': 'ready', 'automation': 'approval-enforced', 'auth': 'required'}


@app.get('/api/readyz')
def readyz():
    """Readiness probe: verifies the database is reachable, not just that the process is up."""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        return {'status': 'ready'}
    except Exception as e:
        return JSONResponse({'status': 'not_ready', 'detail': str(e)}, status_code=503)


@app.get('/api/whoami')
def whoami(principal: Principal = Depends(require_principal)):
    return {'subject': principal.subject, 'tenant_id': principal.tenant_id, 'roles': list(principal.roles),
            'auth_type': principal.auth_type, 'display_name': principal.display_name, 'email': principal.email,
            'scopes': list(principal.scopes)}


@app.get('/api/agents')
def agents(principal: Principal = Depends(require_principal)):
    return registry.describe()
