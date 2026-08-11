# Qarar Product Audit

Date: 2026-08-11  
Branch: `feat/bilingual-ux-production-hardening`  
Baseline: `c6251b2`

## Product and architecture

Qarar is a bilingual enterprise decision-intelligence platform for Saudi and Arabic-market organizations. A Next.js 16 App Router frontend acts as a BFF for a FastAPI service. PostgreSQL/pgvector is the production datastore, Alembic owns schema evolution, and local/S3-compatible object storage holds evidence. API-key/OIDC authentication, tenant-scoped queries, role gates, audit events, an MCP gateway, optional n8n automation, and optional AI providers form the integration boundary.

Primary roles are executives/approvers, project managers/operators, and developers/administrators. The principal workflow is project → evidence → decision case → expert analysis → clarification → recommendation → human approval → controlled automation.

## Baseline evidence

- Git worktree was clean on `main`; remote was `origin`, GitHub repository `majaber1/qarar-ai-v8-production-candidate`.
- Backend: 59 tests passed in 23.78 seconds. Windows emitted a non-failing pytest temporary-directory cleanup warning after completion.
- Frontend dependency reinstall: blocked locally because a stale Next development server first locked the native SWC binary; after stopping only those repository processes, npm could not finish cache/network restoration within 180 seconds. Independent GitHub Actions verification on this feature branch passed dependency installation, type-check, production build, and production dependency audit.
- Hosted frontend: reachable on Vercel. Its transparent connection state reports that no public backend is configured.

## Module matrix

| Module | User purpose | Status | Missing or broken behavior | Root cause | Selected resolution | Verification evidence |
|---|---|---|---|---|---|---|
| Application shell | Navigate major workspaces | Improved | Mobile navigation expanded vertically and lacked a true toggle | Static desktop-first header | Added accessible collapsible menu, active-page state, skip link, and focus treatment | Type review; browser verification required after deployment |
| Localization | Arabic/English parity | Improved | Raw statuses, urgency values, dates, footer, and workflow labels mixed languages | Localization was page-local string selection | Central status/urgency/locale helpers; bilingual footer and workflow labels | Source audit; CI and browser matrix required |
| Operator dashboard | Portfolio and queue command center | Working | Backend enums leaked into cards/table | UI rendered API identifiers directly | Localized labels and locale-aware dates; accessible progress values | Existing production route plus source review |
| Live decision run | Observe expert orchestration | Fixed | Arabic-only operational screen | Page predated shared localization | Full Arabic/English state, metric, empty, failure, and completion copy | Source review; authenticated live run remains environment-dependent |
| Cost studio | Model unit economics | Fixed | English-only page and unlabeled range inputs | Standalone internal tool | Full bilingual copy, LTR numeric islands, accessible range labels | Source review |
| Case detail | Clarify, compare, and approve | Improved | English-only section labels and raw status/urgency values | Hardcoded workflow metadata | Shared localized metadata and bilingual section labels | Source review |
| Authentication/profile | Register, sign in, manage profile | Working | No password-recovery backend contract | Recovery endpoint and email provider are absent | Documented limitation; no fake reset flow added | Existing backend authentication tests |
| Knowledge | Upload and query evidence | Working with configuration | Hosted upload/search unavailable without API, database, and storage | External production services are not configured | Transparent errors retained; exact deployment variables documented | Backend tests and frontend health route |
| Automation/connectors | Execute approved decisions | Working with configuration | External callbacks and connectors require credentials/services | Intentional secure integration boundary | Dry-run/disabled defaults retained; no claims without external tests | Backend security and workflow tests |
| Deployment | Publish frontend and services | Partially ready | Public Vercel frontend has no production API | `QARAR_BACKEND_URL`/backend infrastructure absent | Preserve health banner and document exact requirement | `/api/deployment-health` reports configuration state |

## Known external requirements

1. Deploy FastAPI with PostgreSQL/pgvector and durable object storage.
2. Set Vercel `QARAR_BACKEND_URL` to the public backend URL including `/api`.
3. Configure real AI, email, OIDC, MCP, automation, and malware-scanning credentials only for the integrations being enabled.
4. Validate password recovery only after a recovery contract and transactional email provider are deliberately added.
