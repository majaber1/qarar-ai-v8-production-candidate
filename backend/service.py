"""Vercel Services entrypoint.

Vercel strips the ``/api`` service prefix before invoking the ASGI app. The
existing Qarar application intentionally keeps ``/api`` in its public route
contracts, so this wrapper restores that prefix without changing local,
container, or standalone-backend behavior.
"""

from app.main import app as qarar_app


class ApiPrefixAdapter:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") in {"http", "websocket"}:
            scope = dict(scope)
            path = scope.get("path", "/")
            scope["path"] = f"/api{path if path.startswith('/') else '/' + path}"
            raw_path = scope.get("raw_path")
            if raw_path is not None:
                scope["raw_path"] = b"/api" + raw_path
        await self.app(scope, receive, send)


app = ApiPrefixAdapter(qarar_app)

__all__ = ["app"]
