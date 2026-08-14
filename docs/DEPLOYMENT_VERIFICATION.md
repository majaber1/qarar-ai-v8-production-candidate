# Deployment verification — 2026-08-14

| Item | Verified value |
|---|---|
| Repository | `majaber1/qarar-ai-v8-production-candidate` |
| Source branch | `codex/accelerator-readiness` |
| Vercel team | `20262030-` (`20262031`) |
| Vercel project | `qarar-ai-v8-production-candidate` |
| Root Directory | `frontend` |
| Production URL | `https://qarar-ai-v8-production-candidate.vercel.app` |
| Production pages | `/`, `/project`, and `/cases/new` return HTTP 200 |
| Data platform | Neon `neon-bronze-nest` / `qarar_production`; Alembic `d83a1f0c9200`; pgvector enabled |
| Backend project | `qarar-ai-backend`; Root Directory `backend`; public URL `https://qarar-ai-backend.vercel.app` |
| Backend binding | `QARAR_BACKEND_URL=https://qarar-ai-backend.vercel.app/api` for Production and Preview |
| Live health | Frontend `/api/deployment-health`: HTTP 200, frontend/backend `ready`; backend `/api/health`: HTTP 200, PostgreSQL and auth enabled |
| Object storage | Local and S3-compatible adapters are implemented and tested; durable production S3 credentials are not provisioned |

GitHub recorded successful Vercel Production deployments for both projects against the authoritative branch commit. Both projects track `codex/accelerator-readiness`; their Root Directories are `frontend` and `backend`. The stable aliases are public while API data routes require application authentication. Local HEAD, GitHub branch HEAD, and the deployed frontend source SHA are compared after the final documentation commit rather than embedding a self-referential SHA here.

The frontend-to-backend production link, Neon database, CORS and API authentication are live and health-checked. Full production sign-off remains conditional only for upload durability: the Vercel backend currently uses ephemeral local storage because no S3-compatible credentials were supplied. No secret was committed or substituted with an insecure fallback.
