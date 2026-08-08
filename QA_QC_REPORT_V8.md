# Qarar AI V8 QA/QC Report

Date: 2026-08-08

## Outcome

V8 resolves the material merge conflicts found between the uploaded V6 archive and the partial V7 candidate. It is a substantially stronger production candidate, but final production approval still requires the full dependency-backed suite, Docker Compose validation and a PostgreSQL/n8n staging run in the target environment.

## Evidence executed in this workspace

| Gate | Result |
|---|---|
| Python compile (`app`, `tests`) | Pass |
| Backend tests available with current runtime | 45 passed, 2 deselected |
| New V8 security/integration tests | 5 passed |
| Full original suite | 40 passed; 2 failed and 3 errored only because PyJWT/MCP packages were unavailable in this runner |
| Knowledge upload → ingest → council evidence/citation | Pass |
| Alembic single head | Pass: `a8c4e2f90111` |
| Alembic empty DB upgrade | Pass |
| Alembic current/check | Pass; no new operations |
| Frontend TypeScript | Pass |
| Next.js production build | Pass; 16 static/dynamic routes generated |
| Production dependency audit | Pass; 0 vulnerabilities |
| Docker Compose validation | Not run: Docker CLI unavailable in this workspace |

## Residual release gates

1. Install `backend/requirements.txt` in a clean Linux environment and run all 50 tests without deselection.
2. Run MCP subprocess integration against the pinned installed MCP SDK.
3. Run OIDC tests with PyJWT/cryptography installed.
4. Validate and build Compose with real non-default secrets.
5. Run `alembic upgrade head` against staging PostgreSQL with pgvector.
6. Exercise a real approved-case n8n workflow whose callback signs the raw JSON body exactly as documented.

No area is rated 9/10 because the target Docker/PostgreSQL/n8n environment was not available for complete evidence.
