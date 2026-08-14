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
| Backend binding | Not configured: `/api/deployment-health` returns HTTP 503 with missing `QARAR_BACKEND_URL` |
| Object storage | Local and S3-compatible adapters are implemented and tested; production S3 credentials are not provisioned |

GitHub recorded the successful Vercel Production deployment against the authoritative branch commit. The immutable deployment URL is authentication-protected while the stable production alias is public. Local HEAD, GitHub branch HEAD, and the deployed source SHA must be compared after the final documentation commit; the release report records those values rather than embedding a self-referential SHA in this commit.

The frontend deployment is valid and public, but full-stack production sign-off remains conditional until an authorized Vercel environment write configures `QARAR_BACKEND_URL` and a secure backend deployment receives Neon, authentication, CORS, and durable object-storage secrets. No secret was committed or substituted with an insecure fallback.
