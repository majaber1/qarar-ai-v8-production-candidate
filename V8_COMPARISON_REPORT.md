# V6 + V7 → V8 Comparison

## Merge decision

V8 is based on V6 because V6 contains the newer platform capabilities: PostgreSQL/pgvector migrations, OIDC, malware scanning, expanded MCP, persisted automation runs, role dashboards, clarification workflow and broader tests. The partial V7 candidate contributed targeted security and frontend hardening. V8 is a new line and does not overwrite either input.

| Capability | V6 | Partial V7 | V8 decision |
|---|---|---|---|
| PostgreSQL/pgvector and migration chain | Stronger | Incomplete migration | Keep V6 chain; add V8 callback migration |
| Knowledge Fabric | Rich implementation, not wired into council | Limited | Wire tenant/case retrieval into every council run and return citations |
| Normal/live parity | Divergent | Partial fixes | Enforce budget, AI rate, retrieval, clarification and audit on both |
| MCP | 15 tools and gateway; `httpx2` defect | Smaller surface | Keep V6 surface, fix client import, remove admin from service key |
| Automation | Approval records and callbacks; shared callback key | Some URL hardening | Keep approval persistence; add allowlist, HMAC, expiry and replay defense |
| Object storage | Traversal risk | Safer local paths | Use resolved-root validation and safe S3 keys |
| Frontend | More complete role pages, vulnerable Next 15 | Newer dependency baseline | Keep V6 pages; upgrade to Next 16.3.0; remove callback URL exposure |
| Production schema ownership | `create_all` always | Conditional | Alembic owns non-development schemas |

## Notable V8 changes

- Decision Council now retrieves up to eight case/global evidence chunks scoped to the authenticated tenant.
- Retrieved text is framed as untrusted data before model use; source id, title, reference and trust level remain available for citations.
- Usage records are persisted per agent; audit/usage persistence failures are logged.
- Automation outbound redirects are disabled and webhook hosts must be allowlisted.
- Callback tenant identity is derived from the persisted run, not accepted from the external payload.
- Callback status is an enum and replay nonces are stored under a unique database constraint.
- Uploads cannot attach evidence to another tenant's case.
- API inputs validate urgency and language.
- Backend/frontend containers run non-root; frontend uses a production build.
