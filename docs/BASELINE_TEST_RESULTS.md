# Baseline Test Results

Date: 2026-08-09  
Branch: `main`  
Baseline commit: `e6770f6`

| Gate | Result | Evidence |
|---|---|---|
| Backend tests | PASS | 54 passed after Module 1 profile/security coverage |
| Python compilation | PASS | `app` and `tests` compile |
| API/auth/tenant tests | PASS | Included in backend suite |
| MCP subprocess integration | PASS | Included in the successful 53-test baseline |
| Frontend TypeScript | PASS | `tsc --noEmit` |
| Next.js production build | PASS | 21 routes including profile |
| Production dependency audit | PASS | 0 vulnerabilities |
| Alembic current | PASS | `c9b7e4a812f0 (head)` |
| Alembic check | PASS | No new upgrade operations |
| Docker availability | PASS | Docker 29.6.2, Compose 5.3.1 |
| Backend container image | PASS | Clean Compose build completed |
| MCP container image | PASS | Clean Compose build completed |
| Frontend container image | ENVIRONMENT BLOCKED | `.dockerignore` reduced context from 449 MB to 161 KB and the image reached `next build`; the local Docker daemon then disconnected again with RPC EOF |
| Hosted end-to-end flow | BLOCKED | No public `QARAR_BACKEND_URL`, PostgreSQL or durable object store configured |

## Warnings and concerns

- Pytest reports a Windows temporary-directory cleanup `PermissionError` after successful completion. It does not fail tests or affect application data.
- The frontend deploys successfully but API-backed operations cannot work publicly while the backend URL defaults to localhost.
- The frontend Dockerfile/build inputs are now lean; the remaining container-build failure is a local Docker daemon RPC disconnect, not a source compilation error.
- No repository CI workflow exists; all checks are currently manual.
- Scoring uses fixed global weights and silently treats missing criterion scores as zero.
- Confidence is not yet deterministically calibrated from evidence completeness and option differentiation.

## Critical workflow verified by tests

Registration request → admin approval → password login → profile update/password rotation → project → case → project/case-scoped file → analysis/approval boundaries → logout/session revocation.
