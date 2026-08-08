# Qarar Full Repository Audit

Date: 2026-08-09  
Audited commit: `e6770f6`  
Target version: `8.1.0-beta.1`

## Architecture verified from code

- Frontend: Next.js 16 App Router, React 19, TypeScript, bilingual RTL/LTR interface.
- Backend: FastAPI, SQLAlchemy, Pydantic, tenant-scoped REST and MCP interfaces.
- Data: SQLite for development/tests; PostgreSQL/pgvector intended for production; Alembic owns production schema.
- Identity: API keys, OIDC scaffold, and password sessions with administrator approval.
- Knowledge: project/case-scoped uploads, object-storage abstraction, chunking, hybrid retrieval, trust levels, and malware-scan hooks.
- Decisions: dynamic specialist planning, clarification gate, analysis, recommendation, executive approval, automation callback, audit and usage ledgers.
- Deployment: Docker Compose for the full stack; Vercel currently hosts the frontend only.

Legend: GREEN = production-ready in current scope, YELLOW = incomplete, RED = broken/blocking, GRAY = not implemented.

| Module | Exists | Works | Missing | Bugs | UX Issues | Tests | Risk | Priority |
|---|---|---|---|---|---|---|---|---|
| Authentication & profile | GREEN | Registration request, approval, login/logout, profile and password change | Password reset, MFA, email verification, production IdP | None known after Module 1 fixes | Admin approval route is not linked from normal navigation | Covered | Medium | P0 complete for beta |
| Projects | GREEN | Create/list/get with tenant isolation | Update, archive, membership | No project detail page | Limited project management | Covered | Medium | P1 |
| Decision creation | YELLOW | Plain-language create/list/get and project link | Update, archive, delete, deadline input, ownership policy | Status lifecycle is incomplete | Still asks type before free text | Partial | High | P0 next |
| Context gathering | YELLOW | Clarification gate detects missing information | Editable structured context and progressive intake | Context remains embedded in case/analysis JSON | Questions are not shown before initial case creation | Partial | High | P0 |
| Decision lenses | YELLOW | Specialist agents cover multiple domains | Formal extensible lens model and applicability rules | No persisted lens configuration | Technical agent terms leak in advanced views only | Partial | High | P1 |
| Options | YELLOW | Options agent generates alternatives | Persisted user/AI/hybrid options and editing | Assumes analysis-generated option structure | Editing is absent | Partial | High | P1 |
| Scoring | RED | Fixed weighted calculation exists | Configurable criteria, validation, normalization, evidence and tie rules | Missing scores become zero; weights are global and fixed | Score rationale is not transparent enough | Minimal | Critical | P0 |
| Tradeoffs | YELLOW | Recommendation contains comparison content | Dedicated tradeoff model/view | Not reproducibly derived from scoring | Mixed into long reports | Partial | High | P1 |
| Risk | YELLOW | Risk specialist and risk outputs exist | Editable risk register, likelihood/impact/residual risk | Risk certainty is qualitative | No simple per-option risk editor | Partial | High | P1 |
| AI provider | YELLOW | OpenAI Responses client plus mock fallback | Provider interface for additional vendors | Single live provider implementation | Normal users mostly shielded | Partial | Medium | P2 |
| Recommendation | YELLOW | Recommendation, evidence, confidence and reasons | Stronger sensitivity/assumption contract | Confidence can depend on generated content | Executive copy improved but incomplete | Covered indirectly | High | P1 |
| Confidence | RED | Numeric confidence is displayed | Deterministic composition from completeness/evidence/differentiation | No calibrated formula | Explanation is inconsistent | No dedicated tests | Critical | P0 |
| Sensitivity analysis | GRAY | No | No | Entire feature missing | No “what could change this?” view | None | High | P1 |
| Approval | YELLOW | Executive-only approval with owner/due date | Reject, defer, reopen, comments, reason | Status model supports too few transitions | Approval experience is basic | Covered | High | P1 |
| Action plan | YELLOW | Analysis can suggest next actions; automation gate exists | Persisted actions, owners, dependencies, completion | Suggestions are not workflow records | No action-management view | Partial | High | P1 |
| Follow-up & outcomes | GRAY | Concepts appear in generated text | Persisted follow-ups, reminders, outcome and lessons | Entire learning loop missing | No follow-up dashboard | None | High | P1 |
| User dashboard | YELLOW | Operator workspace and case list | Waiting-input, next action, recently approved and follow-ups | Counts depend on reachable backend | Project/case hierarchy is shallow | Partial | Medium | P1 |
| Executive dashboard | YELLOW | Separate executive surface and approval list | Cycle time, departments, outcomes and implementation | Analytics model absent | Correctly separated from telemetry | Partial | Medium | P2 |
| Admin/operations | YELLOW | Developer metrics, MCP registry, access approval | Central error/queue/health console | Operational data is fragmented | Technical by design | Partial | Medium | P2 |
| Evidence & sources | YELLOW | Upload, trust, project/case scope, citations, scan hooks | URL ingestion, spreadsheets preview, delete/version controls | Local storage is unsuitable for serverless production | Upload flow is now clear | Covered | High | P1 |
| Templates | GRAY | Category field only | Reusable decision templates | Not implemented | No templates navigation | None | Medium | P2 |
| Analytics | YELLOW | Audit events and usage ledger | Privacy-safe product event schema and reporting | Event names are backend-oriented | No analytics consent/admin view | Partial | Medium | P2 |
| Docker/deployment | YELLOW | Backend/frontend/Postgres/MinIO Compose definition | Verified image build and hosted backend | Frontend production cannot reach localhost backend | Public frontend is partially functional | Config only | Critical | P0 infrastructure |
| CI/CD | RED | No workflow | Test/build/migration/security pipeline | Every push depends on manual checks | N/A | None | Critical | P0 |
| Documentation | YELLOW | Architecture, deployment and security docs | Versioned release and operations handbook | README still describes V8 broadly | Too technical for new users | N/A | Medium | P1 |

## Prioritized issues

1. Deploy FastAPI with PostgreSQL and durable object storage; configure `QARAR_BACKEND_URL` in Vercel.
2. Replace the fixed scoring function with validated, reproducible per-case criteria.
3. Complete decision lifecycle: edit/archive, status transitions, rejection/defer/reopen.
4. Add sensitivity analysis, persisted action plans, follow-ups and outcomes.
5. Add CI for tests, migration checks, frontend build and dependency audit.
6. Complete project management and evidence lifecycle operations.

## Production readiness statement

Qarar is a credible beta with strong tenant isolation, an auditable analysis pipeline and a polished role-based frontend. It is not production-ready as a complete hosted product because the public frontend has no deployed backend, scoring/confidence are not sufficiently reproducible, and the execution/outcome loop remains incomplete.
