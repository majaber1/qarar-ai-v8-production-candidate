# Qarar AI V8 — Deployment Guide

## Production topology

The Vercel project hosts the Next.js frontend only. A complete production deployment also requires a separately hosted FastAPI service, PostgreSQL/pgvector, and S3-compatible durable object storage.

Before promoting the frontend, configure the server-only `QARAR_BACKEND_URL` in Vercel for Production and Preview. It must include the backend `/api` suffix. The value is never exposed to the browser.

Use `GET /api/deployment-health` on the frontend as the deployment probe. It returns `503` with `backend: not_configured`, `unreachable`, or `not_ready` until the backend and database are healthy.

## Docker Compose (recommended)

```bash
# Core stack: PostgreSQL + API + MCP + Frontend
docker compose up -d

# With automation (n8n)
docker compose --profile automation up -d

# With malware scanning (ClamAV)
docker compose --profile security up -d

# Full stack
docker compose --profile automation --profile security --profile platform up -d
```

## Vercel FastAPI service

The `backend` directory is independently deployable as a Vercel Python project. Keep it as a separate project from the linked `frontend` project so the existing Next.js build and domain are not replaced.

Required production variables are `ENVIRONMENT=production`, a pooled PostgreSQL `DATABASE_URL`, a non-development `QARAR_API_KEYS_JSON` or production OIDC configuration, and the canonical frontend origin in `CORS_ORIGINS`. Run `python -m alembic upgrade head` against the production database before directing frontend traffic to the service.

After the backend deployment is ready, set the frontend project’s server-only `QARAR_BACKEND_URL` to `https://<backend-domain>/api` for Production and Preview, then redeploy the frontend. Never use SQLite or local object storage for production writes on Vercel because function filesystems are ephemeral.

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `sqlite:///./qarar.db` | PostgreSQL or SQLite connection string |
| `QARAR_API_KEYS_JSON` | Yes | `{}` | JSON mapping API keys to tenant/roles |
| `AUTH_REQUIRED` | No | `true` | Require authentication on all endpoints |
| `AI_API_KEY` | No | | OpenAI/Anthropic API key for real AI |
| `AI_PROVIDER` | No | `mock` | Currently `openai` or `mock` |
| `OIDC_ENABLED` | No | `false` | Enable OIDC JWT validation |
| `OIDC_ISSUER` | No | | OIDC issuer URL |
| `OIDC_JWKS_URL` | No | | JWKS endpoint URL |
| `OIDC_AUDIENCE` | No | | Expected JWT audience |
| `MALWARE_SCAN_ENABLED` | No | `false` | Enable ClamAV scanning |
| `CLAMAV_HOST` | No | `localhost` | ClamAV daemon host |
| `CLAMAV_PORT` | No | `3310` | ClamAV daemon port |
| `MCP_API_KEY` | No | | Key for MCP service connections |
| `AUTOMATION_ENABLED` | No | `false` | Enable n8n automation |
| `N8N_BASE_URL` | No | `http://localhost:5678` | n8n instance URL |
| `RATE_LIMIT_ENABLED` | No | `true` | Enable rate limiting |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `QARAR_BACKEND_URL` | Yes | `http://localhost:8000/api` | Backend API URL |
| `QARAR_DEV_AUTO_LOGIN_KEY` | No | | API key for dev auto-login |

## Database Setup

### PostgreSQL (production)

```bash
# Create database with pgvector extension
psql -c "CREATE DATABASE qarar;"
psql -d qarar -c "CREATE EXTENSION vector;"

# Run migrations
cd backend
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/qarar python -m alembic upgrade head
```

### SQLite (development)

No setup needed — tables auto-created on first run.

## Seed Demo Data

```bash
cd backend
python scripts/seed_demo.py  # Creates 4 sample cases with evidence
```

## Health Checks

- `GET /api/health` — authenticated, full system status
- `GET /api/readyz` — unauthenticated, database reachability probe
- Frontend `GET /api/deployment-health` — verifies Vercel configuration and backend readiness

## Required release gates

The repository CI enforces backend tests and compilation, Alembic upgrade/check, frontend typecheck/build/audit, and Compose configuration validation. Production infrastructure still requires operator-supplied credentials; never commit them to the repository.
