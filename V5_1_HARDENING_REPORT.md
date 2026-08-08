# V5.1 Hardening Report

## Independent-review P0 disposition

| Finding | V5.1 status |
|---|---|
| No REST authentication | Fixed — API-key identity reference implementation + roles |
| No MCP authentication | Fixed — ASGI auth before MCP dispatch |
| Automation approval bypass | Fixed — persisted server-side DecisionApproval verification |
| MCP gateway tuple crash | Fixed — SDK 2.x two-stream handling, tolerant of extra metadata |
| Pydantic/MCP dependency conflict | Fixed in requirements — `pydantic>=2.12,<3` |
| No tenant isolation | Fixed for cases, knowledge, MCP and automation paths |
| Vulnerable Next 15.5.7 | Updated to Next 15.5.22 + React 19.1.8 |

## Additional hardening

- browser BFF prevents publishing a backend API key through `NEXT_PUBLIC_*`
- local `/login` reference flow stores the access key HttpOnly/SameSite Strict
- non-development startup refuses an empty key registry or known `change-me` keys
- Trust A cannot be self-declared through ordinary file upload
- SQLite migration helper added for local V5 data
