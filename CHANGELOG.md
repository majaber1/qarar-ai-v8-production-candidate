# Changelog

## 10.0.0-beta.1 — 2026-08-21

- **Accelerator Readiness Production Hardening**: Single public application URL (`https://qarar-ai-v10.vercel.app`) with server-side proxy architecture to internal FastAPI backend (`qarar-ai-backend`).
- **Complete End-to-End Decision Journey**: Verified full 20-step decision lifecycle from authentication to mandatory qualification gates, evidence citations, score provenance inspector, multi-scenario recalculation, human overrides, executive approvals, action trackers, and outcome evaluations.
- **Bilingual & Responsive Excellence**: 100% test pass rate across 12 Playwright E2E suites covering Desktop and Mobile (Pixel 7) form factors in both Arabic (RTL) and English (LTR).
- **Enterprise Security & Role Governance**: Strict role-based access control (`project_manager`, `developer`, `executive`, `admin`) enforced with tamper-evident audit logging and secure PBKDF2 session authentication.
- **Deterministic Decision Engine**: Authoritative Python scoring engine with evidence-backed provenance, sensitivity matrix recalculation, and zero AI hallucination in ranking mathematics.

## 9.0.0-beta.1 — 2026-08-21

- **Evidence → Score Provenance**: Every score in the evaluation matrix contains deep mathematical and factual provenance linking raw score, normalized score, weight contribution, assessment method, rationale, cited knowledge sources, trust ratings (A/B/C/D), and audit actor.
- **Mandatory Qualification Gates**: Configurable pass/fail thresholds that automatically disqualify non-compliant options while preserving raw and normalized scores for audit and compliance inspection.
- **Five Standard Decision Templates**: Pre-configured enterprise templates (Cloud Platform Selection, Cybersecurity MDR, Tender / Contractor Award, Regional Expansion, AI Initiative Portfolio).
- **Five Business Scenarios**: Multi-perspective evaluation presets (Balanced, Risk & Compliance, Cost & Financial, Speed / Time-to-Value, Strategic Growth) with instant sensitivity comparison.
- **Human Review & Score Overrides**: Authorized human overrides with mandatory justification, automated deterministic recalculation, and recommendation stale detection.
- **Visual Criteria Builder & Options Editor**: Interactive UI components for configuring weighted criteria, direction, scales, mandatory gates, and custom candidate paths.
- **Database & Schema Upgrades**: Added `options`, `score_provenance`, and `override_history` JSON fields with clean Alembic migration `e1f9a2b3c4d5_v9_decision_provenance.py`.
- **Authoritative Deterministic Engine**: 100% deterministic Python scoring engine maintains full authority over final rankings and scenario calculations.

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
