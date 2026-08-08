# Qarar AI V5 — Test Report

Build validation date: 2026-08-07.

## Verified in the build environment

- Python syntax compilation: **0 errors** across backend Python files.
- Backend automated tests: **14/14 passed**.
- FastAPI application import: **passed**.
- HTTP smoke endpoints:
  - `/` → 200
  - `/api/health` → 200
  - `/api/platform/catalog` → 200
  - `/api/connect/catalog` → 200
  - `/api/fabric/research/status` → 200
- Automation dry-run: **passed** and returned `dry_run`.
- Existing planner/orchestrator regression tests from prior versions remain included and passed in this suite.
- V5 tests cover chunking, lexical retrieval, research modes, connector catalog and MCP configuration loading.

## Not verified in the build environment

- The environment package mirror did not provide the new `mcp` v2 package, so the MCP server could not be executed here. `backend/requirements.txt` requests the official current stable v2 line; test it locally with `mcp dev app/mcp_server.py` after installation.
- Full Next.js build could not be executed because this environment's npm mirror returns 404 for `@types/node@22.10.2`. Frontend source was generated from the already-working V4/V3.1 base, but a local `npm install && npm run build` is still required.
- Live Microsoft 365 / Google OAuth cannot be verified without customer app registrations and credentials.
- Live GitHub MCP requires its host credentials and configuration.
- Public/official web research is disabled by default and needs provider configuration.
- Live n8n execution requires an actual n8n workflow and `AUTOMATION_ENABLED=true`; only the safe dry-run path was verified.
- S3/MinIO adapter requires an object store instance; local filesystem object storage is the zero-config default.

## Pilot readiness interpretation

V5 is a **reference platform foundation / design-partner build**, not a production government deployment. Before an external production rollout, complete the P0/P1 security and identity items in `docs/SECURITY_BOUNDARIES.md` and run the independent Claude Code / Codex review prompt included in the repository.
