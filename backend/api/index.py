"""Vercel Python Function entrypoint for the Qarar FastAPI production API."""

from app.main import app

__all__ = ["app"]
