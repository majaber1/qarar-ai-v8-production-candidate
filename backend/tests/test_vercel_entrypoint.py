from fastapi import FastAPI


def test_vercel_entrypoint_exports_fastapi_app():
    from index import app

    assert isinstance(app, FastAPI)
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/api/readyz" in paths
    assert "/api/health" in paths
