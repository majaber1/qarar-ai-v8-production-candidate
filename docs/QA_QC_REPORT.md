# QA/QC report — 2026-08-14

Release recommendation: **READY WITH DISCLOSED LIMITATIONS**.

| Gate | Result | Evidence |
|---|---|---|
| Backend regression | PASS | 66 tests in 31.70s using the declared dependency set |
| Alembic upgrade | PASS | Empty disposable database upgraded through revision `d83a1f0c9200` |
| Schema drift | PASS | `alembic check`: no new upgrade operations detected |
| Generated schema | PASS | Criteria/calculation metadata plus action, outcome and evidence-version columns/tables/indexes verified in SQLite metadata |
| Frontend type-check | PASS | `tsc --noEmit` |
| Production build | PASS | Next.js 16.3.0; 22 pages generated |
| Frontend lint | PASS | ESLint: 0 errors; 6 non-blocking legacy hook warnings |
| Automated browser E2E | PASS | Playwright: Arabic/English × Desktop Chrome/Pixel 7, 4/4 passed |
| Manual golden path | PASS | Arabic/English and desktop/mobile; clarification, analysis, sensitivity, action, approval, completion and outcome |
| Dependency audit | PASS | Final `npm audit --omit=dev --audit-level=high`: zero vulnerabilities; earlier `ECONNRESET` was transient |
| PostgreSQL/pgvector | PASS | Neon `neon-bronze-nest`, `qarar_production`, revision `d83a1f0c9200`, pgvector enabled |
| Hosted full-stack path | BLOCKED EXTERNALLY | Backend URL, frontend backend binding, and durable object-storage credentials not yet confirmed |

## Calculation verification

Criterion normalization uses `(bounded_raw - min) / (max - min) × 100`, inverted for `lower_better`. The weighted score is `Σ(normalized × weight) / Σ(included weights)`. `incomplete` missing values invalidate an option; `exclude` values are omitted and remaining weights are renormalized. The tie threshold is 0.01.

Sensitivity is highly sensitive when the leader changes or the scenario margin is below 2 points, moderately sensitive below 8, otherwise stable.

Deterministic confidence is:

`0.15 context + 0.12 evidence coverage + 0.12 source quality + 0.18 scoring completeness + 0.10 option differentiation + 0.10 clarification resolution + 0.08 assumption control + 0.07 conflict control + 0.08 sensitivity stability`

The implementation returns the nine factors, positives, uncertainties and improvement actions. Model-reported confidence is not part of this calculation.

## Coverage highlights

- Criterion scales/directions, missing policies, ties and sensitivity leader changes.
- Valid/invalid lifecycle transitions and executive-only approval/rejection.
- Tenant isolation for cases, projects, evidence, actions and outcomes.
- Action dependency/status/completion behavior and approved-decision outcome precondition.
- Project updates/archive summaries and evidence metadata/replacement/deletion.
- Bilingual direction switching, confidence/sensitivity/action rendering and mobile menu behavior.

## Deployment findings

- The authoritative frontend project is `qarar-ai-v8-production-candidate` under Vercel team `20262030-`; Root Directory is `frontend` and the production branch is `codex/accelerator-readiness`.
- Frontend and backend `vercel.json` files are structurally present.
- No repository Vercel link metadata was found, so the target account/project cannot be safely inferred locally.
- Neon PostgreSQL is verified against `neon-bronze-nest`: `qarar_production` is migrated to `d83a1f0c9200` and pgvector is enabled. Durable S3-compatible persistence remains unconfigured; the verified object lifecycle tests used local storage.
- GitHub Actions passed backend, frontend, and Compose jobs for the release commit. GitHub also recorded a successful Vercel Production deployment; `/`, `/project`, and `/cases/new` return HTTP 200 from the stable alias. `/api/deployment-health` accurately returns HTTP 503 because `QARAR_BACKEND_URL` is not configured.

Production sign-off requires an authorized operator to provision/link the services, apply Alembic to PostgreSQL, configure server-only variables, retain deployment protection or an approved public access policy, and rerun the same Playwright suite against the hosted URL.
