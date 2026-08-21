# Qarar frontend deployment

This directory is the Root Directory of the Vercel project `qarar-ai-v8-production-candidate`. Production tracks `codex/accelerator-readiness` and uses the server-only `QARAR_BACKEND_URL` environment variable to proxy authenticated requests to the separately deployed FastAPI service.

The public production URL is `https://qarar-ai-v8-production-candidate.vercel.app`. Verify `/api/deployment-health` after every environment or backend change; a release-ready response reports both `frontend` and `backend` as `ready`.
