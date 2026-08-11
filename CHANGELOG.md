# Changelog

## 8.2.0-beta.1 — 2026-08-11

- Added validated, normalized per-case scoring weights; incomplete scores are now explicit instead of silently treated as zero.
- Replaced generated confidence with a deterministic evidence/coverage/separation formula and an explainable breakdown.
- Added audited case editing and archive, defer, reject, and reopen transitions.
- Added a complete GitHub Actions quality gate for backend, migrations, frontend, dependency audit, and Compose configuration.
- Added Vercel deployment health reporting and resilient `503` responses when the separately hosted backend is unavailable.
- Added the Alembic migration and regression tests for scoring and lifecycle behavior.
- Rebuilt the operator workspace as a responsive portfolio dashboard with live KPIs, decision pipeline, searchable work queue, priority alerts, project progress, and service-health guidance.

## 8.1.0-beta.1 — 2026-08-09

- Added persisted projects and project-scoped decisions and evidence.
- Added administrator-approved password registration, revocable sessions and secure logout.
- Added profile editing and secure password change with full session revocation.
- Prevented account enumeration through duplicate registration responses.
- Added role-separated operator, executive and administrator experiences.
- Added full repository audit, verified baseline and brand guidance.
- Added missing Docker ignore rules after the baseline exposed a 449 MB frontend build context.
- Confirmed the product remains beta until the backend is hosted and scoring, confidence and execution follow-up are completed.
