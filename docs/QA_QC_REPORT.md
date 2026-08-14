# QA/QC report — 2026-08-14

| Check | Result |
|---|---|
| `npm ci --prefer-offline --no-audit` | PASS, 27 packages |
| `npm run typecheck` | PASS |
| `npm run build` | PASS, 22 generated routes |
| `.venv-qa\Scripts\python -m pytest -q --basetemp=.pytest-venv-tmp` | PASS, 60 tests |

The machine-wide Python environment had Pydantic 2.9.2 and was below the repository's declared `>=2.12` range. A disposable local QA environment with Pydantic 2.13.4 was used. The live MCP fixture was changed to discard child-process logs instead of writing to an unread pipe.

Not executed: production migrations, deployed browser E2E, real PostgreSQL/pgvector, real object storage, or external AI/connectors because credentials/endpoints were unavailable.
