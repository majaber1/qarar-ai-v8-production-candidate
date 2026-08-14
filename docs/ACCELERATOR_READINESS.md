# Accelerator readiness

Readiness: **9/10 — product-ready; production integration conditional**.

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

Readiness is calculated from ten equally weighted gates: product flow, explainability, tenant security, evidence lifecycle, data migrations, backend regression, frontend static quality, bilingual responsive E2E, dependency security, and hosted full-stack verification. Nine gates pass; hosted full-stack verification remains conditional, therefore `9 passed / 10 total = 9.0/10`.

## Remaining external release gate

The authoritative frontend project is `qarar-ai-v8-production-candidate` under Vercel team `20262030-`, with Root Directory `frontend` and production branch `codex/accelerator-readiness`. Neon project `neon-bronze-nest` is confirmed: database `qarar_production` is at revision `d83a1f0c9200` and `vector` is enabled. A public backend URL, frontend `QARAR_BACKEND_URL`, durable S3-compatible production credentials, and hosted golden-path execution remain the external release gate.

This is an infrastructure/credential gate, not a hidden application fallback. Until those resources are provisioned and the hosted golden path is executed, label the release **conditional go for production infrastructure; go for accelerator demonstration on the verified local stack**.

Dependency audit is verified: after earlier transient `ECONNRESET` failures, the final `npm audit --omit=dev --audit-level=high` completed with zero vulnerabilities.
