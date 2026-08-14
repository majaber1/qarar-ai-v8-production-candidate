# Accelerator readiness

Readiness: **9.5/10 — hosted full stack ready; durable uploads conditional**.

## What is complete

- A coherent decision loop from draft, clarification and analysis through recommendation, executive approval, action ownership, completion, outcome capture, lessons and archival/reopening.
- Structured per-case criteria with scales, direction, missing-data policies, normalized weights, traceable contributions, deterministic ties and sensitivity scenarios.
- Deterministic confidence based on nine inspectable quality factors; uncalibrated model self-confidence is explicitly excluded.
- Tenant-scoped project, case, evidence, action and outcome APIs with role enforcement and audit events.
- Evidence ownership/review metadata, trust updates, versioned replacement, immediate retrieval exclusion and soft deletion.
- Professional Arabic/English UI with RTL/LTR behavior and responsive desktop/mobile navigation.
- Repeatable backend, migration, frontend build and Playwright browser verification.

## Verified accelerator demo

Sign in → create project/case → answer clarification questions → rerun analysis → compare weighted criteria and evidence → inspect confidence factors → change weights and run sensitivity → submit for approval → executive selects the option/owner/date → generated next actions become persisted work → complete an action → record actual versus expected outcome and lessons → inspect the audit/developer view.

## Scoring formula

Readiness is calculated from ten equally weighted gates: product flow, explainability, tenant security, evidence lifecycle, data migrations, backend regression, frontend static quality, bilingual responsive E2E, dependency security, and hosted full-stack verification. The first nine gates pass. The hosted gate receives half credit because the authenticated backend, Neon database and frontend proxy are live, while durable evidence uploads still need S3-compatible storage: `(9 full gates + 0.5 hosted gate) / 10 = 9.5/10`.

## Remaining external release gate

The authoritative Vercel projects are `qarar-ai-v8-production-candidate` (Root Directory `frontend`) and `qarar-ai-backend` (Root Directory `backend`) under team `20262030-`; both track `codex/accelerator-readiness`. `QARAR_BACKEND_URL` points to the public authenticated backend and the frontend deployment-health route reports both tiers ready. Neon project `neon-bronze-nest` is confirmed: database `qarar_production` is at revision `d83a1f0c9200` and `vector` is enabled. Durable S3-compatible production credentials remain the only infrastructure release gate.

This is an upload-durability infrastructure gate, not a hidden application fallback. Until S3-compatible storage is provisioned, label the release **go for accelerator demonstration and database-backed production flows; conditional for durable evidence uploads**.

Dependency audit is verified: after earlier transient `ECONNRESET` failures, the final `npm audit --omit=dev --audit-level=high` completed with zero vulnerabilities.
