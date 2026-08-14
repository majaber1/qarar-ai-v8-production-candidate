# Accelerator readiness

Readiness: **8/10 — ready with disclosed limitations**.

Completed: bilingual decision workspace, authentication/session proxy, case lifecycle, explainable weighted scoring, evidence and knowledge flows, production frontend build, extensive backend regression suite, deployment configuration.

P0: confirm the public frontend-to-backend-to-PostgreSQL/pgvector-to-object-storage path using production credentials; run critical browser E2E against the deployed environment.

P1: sensitivity analysis, persisted action-plan follow-up/outcomes, and broader CI browser coverage.

P2: polish non-critical advanced connector demonstrations.

Demo flow: sign in; create a case; clarify missing inputs; compare weighted options and evidence; explain confidence and rationale; approve/defer/reopen; show knowledge and audit views.

External dependencies: deployed backend URL, PostgreSQL/pgvector, object storage, AI provider keys, and any enabled MCP/connectors. The product must show a truthful unavailable state when these are absent.

Risk: the repository proves local correctness but does not by itself prove production credentials, persistence, or third-party availability.
