# قرار | Qarar — Decision Intelligence Platform

**Version 8.2.0-beta.1 — قرارات أوضح. بثقة أكبر. / Decide Better.**

Evidence → Decision → Human Approval → Action, with tenant isolation and an auditable trail.

## What V8 combines

V8 uses the richer V6 platform as its base and carries forward the security and frontend fixes from the partial V7 candidate. It adds the missing integration between Knowledge Fabric and Decision Council, normal/live policy parity, signed automation callbacks, safer storage and networking, and a clean Next.js 16 frontend.

| Area | V8 behavior |
|---|---|
| Decision Council | Dynamic experts, scoring, critic and chief recommendation |
| Knowledge Fabric | Tenant/case-scoped hybrid retrieval is injected into every council run with source metadata |
| Live analysis | Same budget, rate-limit, evidence, clarification and audit controls as normal analysis |
| Automation | Approved-case gate, host allowlist, HMAC-SHA256 callback, timestamp and nonce replay protection |
| Data | PostgreSQL/pgvector in production; Alembic is the production schema owner |
| Access | API keys or OIDC, tenant isolation, role gates; MCP service key has no admin role |
| UI | Executive, PM/operator and developer/admin experiences; Arabic/English and RTL/LTR |

## Secure quick start

1. Copy `backend/.env.example` to `backend/.env` for local development and replace every sample secret.
2. For containers, set `POSTGRES_PASSWORD`, `MINIO_ROOT_PASSWORD` and `QARAR_API_KEYS_JSON` in your shell or Compose environment.
3. Apply migrations before starting production services.

```bash
cd backend
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --port 8000

cd ../frontend
npm ci
npm run typecheck
npm run build
npm run start
```

For Docker:

```bash
docker compose config
docker compose build
docker compose up -d
```

## Signed n8n callbacks

Configure the same high-entropy `AUTOMATION_CALLBACK_SECRET` in Qarar and the trusted workflow runtime. The callback sends JSON to `/api/connect/automation/callback/{run_id}` with:

- `X-Qarar-Timestamp`: Unix seconds
- `X-Qarar-Nonce`: unique value for every attempt
- `X-Qarar-Signature`: hex HMAC-SHA256 of `timestamp + "." + nonce + "." + raw_body`

Allowed statuses are `executed`, `failed`, and `cancelled`. Signatures outside the configured skew window and reused nonces are rejected.

## Verification

```bash
cd backend
python -m pytest -q
python -m compileall -q app tests
python -m alembic upgrade head
python -m alembic check

cd ../frontend
npm ci
npm run typecheck
npm run build
npm audit --omit=dev
```

See `V8_COMPARISON_REPORT.md` and `QA_QC_REPORT_V8.md` for merge decisions, evidence, and known verification limits.

Current audit and verified baseline: `docs/QARAR_FULL_AUDIT.md` and `docs/BASELINE_TEST_RESULTS.md`. This release is a beta; the public frontend requires a separately hosted FastAPI backend, PostgreSQL, and durable object storage for full functionality.

Proprietary — Qarar AI Enterprise Platform.
