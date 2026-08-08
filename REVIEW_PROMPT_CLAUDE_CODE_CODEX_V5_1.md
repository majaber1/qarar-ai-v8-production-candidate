# Independent Review Prompt — Qarar AI V5.1

Act as a principal software architect, application-security engineer, MCP interoperability reviewer, AI/RAG engineer, and enterprise SaaS due-diligence reviewer.

Review the actual repository. Do not trust README claims until verified.

## Primary objective

Determine whether V5.1 truly closes the seven P0 findings from the previous V5 review without regressing the working decision engine.

## Mandatory workflow

1. Install backend dependencies from a clean environment.
2. Run all backend tests.
3. Build the frontend and run `npm audit`.
4. Start REST API and test:
   - anonymous `/api/cases` => 401
   - valid key => `/api/whoami` returns expected subject/tenant/roles
   - Tenant A cannot read/analyze Tenant B case
   - role gates work
5. Start MCP server with the official MCP SDK client:
   - anonymous connection/tool call is rejected
   - authenticated client lists tools and calls `health`
   - Tenant A cannot `get_case` for Tenant B
6. Configure Qarar MCP gateway to the local authenticated MCP server and prove:
   - list_tools works
   - call_tool works
7. Test automation:
   - dry run works without approval
   - non-dry-run on unapproved case is rejected even if client sends an `approved=true` extra field
   - approve a case through the executive endpoint
   - non-dry-run then passes the approval gate (mock the n8n network destination if necessary)
   - repeat through MCP to prove MCP cannot bypass the gate
8. Test Knowledge Fabric tenant isolation and confirm direct upload cannot self-assert Trust A.
9. Re-run planner/orchestrator tests to prove irrelevant agents are still skipped and parallel execution still works.
10. Threat-model the new BFF/session/API-key implementation.

## Report

Return:

- Executive verdict
- 0–10 scorecard
- What is genuinely fixed
- What remains unsafe
- Bugs found by actual execution
- REST auth assessment
- MCP auth/server/client assessment
- Tenant/IDOR assessment
- Automation approval assessment
- Knowledge/RAG assessment
- Frontend dependency/audit assessment
- Commercial readiness
- P0/P1/P2/P3 backlog
- Go/No-Go for internal demo, design-partner pilot, government pilot, enterprise production

Explicitly label anything you could not verify. Do not call a stub or configuration point “complete.”
