# قرار | Qarar — Decision Intelligence Platform

**Version 8.2.0-beta.1 — قرارات أوضح. بثقة أكبر. / Decide Better.**

Evidence → Decision → Human Approval → Action, with tenant isolation and an auditable trail.

## What V8 combines

V8 uses the richer V6 platform as its base and carries forward the security and frontend fixes from the partial V7 candidate. It adds the missing integration between Knowledge Fabric and Decision Council, normal/live policy parity, signed automation callbacks, safer storage and networking, and a clean Next.js 16 frontend.

| Area | V8 behavior |
|---|---|
| Decision Council | Dynamic experts, structured per-case criteria, deterministic scoring/confidence, sensitivity analysis, critic and chief recommendation |
| Knowledge Fabric | Tenant/case-scoped hybrid retrieval, trust/review metadata, versioned replacement, and soft deletion |
| Live analysis | Same budget, rate-limit, evidence, clarification and audit controls as normal analysis |
| Automation | Approved-case gate, host allowlist, HMAC-SHA256 callback, timestamp and nonce replay protection |
| Data | PostgreSQL/pgvector in production; Alembic is the production schema owner |
| Access | API keys or OIDC, tenant isolation, role gates; MCP service key has no admin role |
| Decision loop | Draft-to-archive lifecycle, executive approval, persisted owners/actions/dependencies, outcomes, lessons and follow-up summaries |
| UI | Executive, PM/operator and developer/admin experiences; Arabic/English, RTL/LTR, desktop and mobile |

## Explainable calculation model

Each criterion is stored with a weight, scale, direction (`higher_better` or `lower_better`) and explicit missing-value policy. Raw scores are bounded to the configured scale and normalized to 0–100:

`normalized = (bounded_raw - scale_min) / (scale_max - scale_min) × 100`

For `lower_better`, Qarar uses `100 - normalized`. The option score is:

`weighted_score = Σ(normalized_i × weight_i) / Σ(included_weight_i)`

An `incomplete` missing criterion invalidates the score; `exclude` removes its weight from the denominator. Weight totals are normalized to 1. Ties are explicit when the first two scores differ by at most 0.01. Sensitivity recalculates both weights and criterion scores; a leader change or margin below 2 is highly sensitive, a margin below 8 is moderately sensitive, otherwise stable.

Confidence is deterministic and excludes uncalibrated model self-confidence. It is the weighted sum of context completeness (15%), evidence coverage (12%), source quality (12%), scoring completeness (18%), option differentiation (10%), clarification resolution (10%), assumption control (8%), conflict control (7%), and sensitivity stability (8%). The API and UI retain the factor values, positive factors, uncertainties, and concrete improvement actions.

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
npm run lint
npm run typecheck
npm run build
npm run test:e2e
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
npm run test:e2e
npm audit --omit=dev --audit-level=high
```

See `docs/ACCELERATOR_READINESS.md` and `docs/QA_QC_REPORT.md` for release evidence and known verification limits.

Current audit and verified baseline: `docs/QARAR_FULL_AUDIT.md` and `docs/BASELINE_TEST_RESULTS.md`. The public frontend is deployed at `https://qarar-ai-v8-production-candidate.vercel.app` and is bound server-side to the authenticated FastAPI service at `https://qarar-ai-backend.vercel.app/api`. The production data target is Neon `neon-bronze-nest`: database `qarar_production` is at Alembic revision `d83a1f0c9200` with pgvector enabled. Durable S3-compatible object storage is the remaining production infrastructure dependency; the current backend storage setting is local and therefore ephemeral on Vercel.

## Arabic, English, and RTL

The language switcher persists the user's preference locally and applies `lang` plus `dir` to the document. Shared status and urgency labels are localized centrally. UI layout uses logical start/end behavior where direction matters; URLs, IDs, model names, code, and financial values remain readable as LTR islands. When adding copy, provide natural Arabic and English through the shared `useLang()` helpers and test both directions at mobile, tablet, and desktop widths.

## Product audit and release evidence

- `docs/PRODUCT_AUDIT.md` — current module matrix, root causes, resolutions, and external blockers.
- `docs/RELEASE_REPORT.md` — bilingual UX changes, verification results, known limitations, and deployment readiness.

Proprietary — Qarar AI Enterprise Platform.
