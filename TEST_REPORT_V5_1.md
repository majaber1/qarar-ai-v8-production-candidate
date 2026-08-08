# Qarar AI V5.1 — Verification Report

Date: 2026-08-07

## Verification completed in this build environment

### Backend

- Python syntax compile: **75 files / 0 errors**
- Pytest: **24 / 24 passed**
- Manual live REST smoke test:
  - `/api/health` → 200
  - anonymous `/api/cases` → **401**
  - authenticated `/api/whoami` → expected subject/tenant/roles
  - authenticated case create → **201**, tenant and creator persisted from identity

### Security tests added

- unauthenticated REST business endpoints reject access
- tenant A cannot read tenant B case IDs
- role gate blocks a read-only executive identity from running analysis
- Knowledge Fabric sources are tenant-scoped
- ordinary upload cannot self-declare Trust A
- MCP authentication middleware rejects anonymous access and establishes tenant context for valid keys
- non-dry-run automation rejects an unapproved case
- a persisted approval record allows the automation gate to pass
- legacy client `approved=true` is not an authorization mechanism

### Decision-engine regression

Existing planner/orchestrator tests remain green, including:

- 100 planner runs
- irrelevant-agent skipping
- cloud/cyber/data routing
- vendor/legal/procurement routing
- live stream plan/start/done/complete events
- deterministic scoring

### Frontend static verification

- TypeScript/TSX parser check: **25 files / 0 syntax errors**
- Browser architecture changed to same-origin BFF; backend API key is no longer a `NEXT_PUBLIC_*` value.

## Unable to re-run in this build environment

The container's internal package mirrors do not currently provide the required Python/npm packages for a clean install:

- PyPI mirror returned no distribution for even the pinned FastAPI package, so a clean `pip install -r requirements.txt` could not be re-executed here.
- npm mirror returned 404 for `@types/node@22.10.2`, so `npm install && npm run build && npm audit` could not be re-executed here.
- the `mcp` Python package is not present in the base environment and the mirror does not provide it, so the authenticated MCP server/client were not live-started again in this environment.

The V5 independent Claude review already reproduced the MCP 2.0.0 stream return shape and the Pydantic dependency conflict. V5.1 fixes those exact defects, but the official MCP live test should be repeated on the user's workstation and by Claude Code/Codex using `REVIEW_PROMPT_CLAUDE_CODE_CODEX_V5_1.md`.

## Dependency changes

- `pydantic==2.11.7` → `pydantic>=2.12,<3` to satisfy MCP 2.x dependency requirements.
- Next.js `15.5.7` → `15.5.22`.
- React / React DOM → `19.1.8`.

## Release assessment

### Internal demo
GO.

### Controlled design-partner pilot
Conditionally GO after:

1. replace the example development key;
2. repeat clean dependency install on deployment target;
3. repeat official MCP server + gateway live tests;
4. configure customer-specific CORS/MCP origins and secrets;
5. run customer security review.

### Government / enterprise production
Still NO-GO until the documented P1/P2 items are implemented: OIDC/SSO lifecycle, PostgreSQL/formal migrations, malware scanning, durable rate/cost limits, secrets manager, observability/SIEM, durable ingestion workers, and scale-grade vector retrieval.
