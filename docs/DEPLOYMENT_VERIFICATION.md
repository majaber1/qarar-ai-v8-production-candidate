# Deployment verification — 2026-08-21

| Item | Verified value |
|---|---|
| Repository | `majaber1/qarar-ai-v10` |
| Source branch | `main` / `codex/accelerator-readiness` |
| Vercel team | `20262031` (`majaber1`) |
| Frontend project | `qarar-ai-v10` (Project ID: `prj_mlu8LnDKaKbcDe8rLaqvf76M1GD6`) |
| Root Directory | `frontend` |
| Public Product URL | `https://qarar-ai-v10.vercel.app` |
| Production pages | `/`, `/project`, `/cases/new`, and `/executive` return HTTP 200 |
| Data platform | Neon `neon-bronze-nest` / `qarar_production`; Alembic `e1f9a2b3c4d5`; pgvector enabled |
| Backend project | `qarar-ai-backend`; Root Directory `backend`; internal URL `https://qarar-ai-backend.vercel.app` |
| Backend binding | `QARAR_BACKEND_URL=https://qarar-ai-backend.vercel.app/api` for Production and Preview |
| Live health | Frontend `/api/deployment-health`: HTTP 200, frontend/backend `ready`; backend `/api/health`: HTTP 200, PostgreSQL and auth enabled |
| Single Public URL Architecture | Users, demos, and reviewers access ONLY `https://qarar-ai-v10.vercel.app`; API requests proxy server-side to backend |
| Object storage | Local and S3-compatible adapters are implemented and tested; durable production S3 credentials are not provisioned |

GitHub recorded successful Vercel Production deployments for both projects against the authoritative branch commit. Both projects track `codex/accelerator-readiness` and `main`; their Root Directories are `frontend` and `backend`. The single public URL `https://qarar-ai-v10.vercel.app` serves the entire application and proxies API requests seamlessly.

The frontend-to-backend production link, Neon database, CORS, and API authentication are live and health-checked. Full production sign-off remains conditional only for upload durability: the Vercel backend currently uses ephemeral local storage because no S3-compatible credentials were supplied. No secret was committed or substituted with an insecure fallback.
