# Qarar frontend deployment

This directory is the Root Directory of the Vercel project `qarar-ai-v10`. Production tracks `codex/accelerator-readiness` and `main`, using the server-only `QARAR_BACKEND_URL` environment variable to securely proxy authenticated requests to the separately deployed FastAPI backend service.

The single public application URL for users, demos, and accelerator reviewers is `https://qarar-ai-v10.vercel.app`. Verify `/api/deployment-health` after every environment change; a release-ready response reports both `frontend` and `backend` as `ready`.
