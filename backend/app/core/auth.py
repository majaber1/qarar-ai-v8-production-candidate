from __future__ import annotations

import hmac
import hashlib
import json
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Iterable

from fastapi import Header, HTTPException, status

from app.core.config import settings

# Reference role set. Any string is accepted (the registry is just JSON), but these are the
# roles Qarar V8's routes and UI actually branch on.
KNOWN_ROLES = ('executive', 'project_manager', 'analyst', 'developer', 'admin', 'integration_service')


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    roles: tuple[str, ...]
    auth_type: str = "api_key"  # 'api_key' | 'oidc' | 'mcp_api_key' | 'dev_login'
    display_name: str | None = None
    email: str | None = None
    scopes: tuple[str, ...] = field(default_factory=tuple)

    def has_any_role(self, allowed: Iterable[str]) -> bool:
        allowed_set = set(allowed)
        return bool(set(self.roles) & allowed_set) or "admin" in self.roles


_current_principal: ContextVar[Principal | None] = ContextVar("qarar_current_principal", default=None)


def _registry() -> dict[str, dict]:
    try:
        raw = json.loads(settings.qarar_api_keys_json or "{}")
        if not isinstance(raw, dict):
            return {}
        return raw
    except Exception:
        return {}


def authenticate_key(key: str | None) -> Principal | None:
    if not key:
        return None
    for configured_key, meta in _registry().items():
        if hmac.compare_digest(str(configured_key), str(key)):
            roles = meta.get("roles") or []
            if isinstance(roles, str):
                roles = [roles]
            return Principal(
                subject=str(meta.get("subject") or "unknown"),
                tenant_id=str(meta.get("tenant_id") or "default"),
                roles=tuple(str(x) for x in roles),
                display_name=meta.get("display_name"),
                email=meta.get("email"),
                auth_type="api_key",
            )
    # Backward-compatible dedicated MCP service key, mapped to an explicit tenant and the
    # integration_service role (not a blanket admin identity).
    if settings.mcp_api_key and hmac.compare_digest(str(settings.mcp_api_key), str(key)):
        return Principal(subject="mcp-service", tenant_id=settings.mcp_tenant_id,
                          roles=("integration_service",), auth_type="mcp_api_key")
    # Password logins issue opaque, short-lived tokens. Only a SHA-256 digest is stored.
    try:
        from datetime import datetime, timezone
        from sqlalchemy import select
        from app.core.database import SessionLocal
        from app.models.workspace import UserSession, WorkspaceUser
        with SessionLocal() as db:
            row = db.execute(select(UserSession, WorkspaceUser).join(WorkspaceUser, WorkspaceUser.id == UserSession.user_id).where(
                UserSession.token_hash == hashlib.sha256(str(key).encode()).hexdigest(), UserSession.revoked.is_(False),
                UserSession.expires_at > datetime.now(timezone.utc), WorkspaceUser.active.is_(True))).first()
            if row:
                session, user = row
                return Principal(subject=f'user:{user.id}', tenant_id=user.tenant_id, roles=(user.role,),
                                 display_name=user.full_name, email=user.email, auth_type='session')
    except Exception:
        pass
    return None


_jwks_client = None


def _get_jwks_client():
    """Lazily build a PyJWKClient against the configured OIDC JWKS endpoint. Cached per-process."""
    global _jwks_client
    if _jwks_client is None and settings.oidc_jwks_url:
        import jwt
        _jwks_client = jwt.PyJWKClient(settings.oidc_jwks_url)
    return _jwks_client


def authenticate_oidc(token: str | None) -> Principal | None:
    """Validate a bearer JWT against the configured OIDC issuer (e.g. Microsoft Entra ID).

    This is a reference implementation: it validates signature (via JWKS), issuer, and audience,
    then maps the resulting claims onto the same Principal contract used by API keys. Swapping the
    identity provider means changing configuration (issuer/JWKS URL/claim names), not this function's
    callers, or anything in Qarar Core.
    """
    if not settings.oidc_enabled or not token:
        return None
    client = _get_jwks_client()
    if client is None:
        return None
    try:
        import jwt
        signing_key = client.get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token, signing_key, algorithms=["RS256"],
            audience=settings.oidc_audience, issuer=settings.oidc_issuer,
            options={"require": ["sub"]},
        )
    except Exception:
        return None

    tenant_id = str(claims.get(settings.oidc_tenant_claim) or claims.get("tid") or "").strip()
    if not tenant_id:
        return None
    roles = claims.get(settings.oidc_role_claim) or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    scopes = claims.get("scp") or claims.get("scope") or ""
    scopes = tuple(scopes.split()) if isinstance(scopes, str) else tuple(scopes)
    return Principal(
        subject=str(claims.get("sub")), tenant_id=tenant_id, roles=tuple(str(r) for r in roles),
        display_name=claims.get("name"), email=claims.get("email") or claims.get("preferred_username"),
        scopes=scopes, auth_type="oidc",
    )


def _extract_key(x_qarar_api_key: str | None, authorization: str | None) -> str | None:
    if x_qarar_api_key:
        return x_qarar_api_key.strip()
    if authorization:
        parts = authorization.strip().split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1].strip()
    return None


def _authenticate(x_qarar_api_key: str | None, authorization: str | None) -> Principal | None:
    key = _extract_key(x_qarar_api_key, authorization)
    principal = authenticate_key(key)
    if principal:
        return principal
    # A bearer token that doesn't match a configured API key is tried against OIDC when enabled.
    if settings.oidc_enabled and authorization:
        bearer = _extract_key(None, authorization)
        principal = authenticate_oidc(bearer)
        if principal:
            return principal
    return None

def authenticate_headers(x_qarar_api_key: str | None, authorization: str | None) -> Principal | None:
    """Resolve a request principal for middleware without granting or mutating context."""
    return _authenticate(x_qarar_api_key,authorization)


async def require_principal(
    x_qarar_api_key: str | None = Header(default=None, alias="X-Qarar-API-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> Principal:
    principal = _authenticate(x_qarar_api_key, authorization)
    if not principal:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    _current_principal.set(principal)
    return principal


def require_roles(*roles: str):
    async def dependency(
        x_qarar_api_key: str | None = Header(default=None, alias="X-Qarar-API-Key"),
        authorization: str | None = Header(default=None, alias="Authorization"),
    ) -> Principal:
        principal = _authenticate(x_qarar_api_key, authorization)
        if not principal:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if roles and not principal.has_any_role(roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        _current_principal.set(principal)
        return principal
    return dependency


def current_principal() -> Principal:
    principal = _current_principal.get()
    if not principal:
        raise RuntimeError("No authenticated principal in current request context")
    return principal


def set_current_principal(principal: Principal):
    return _current_principal.set(principal)


def reset_current_principal(token):
    _current_principal.reset(token)
