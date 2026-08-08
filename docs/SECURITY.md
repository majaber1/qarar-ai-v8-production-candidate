# Qarar AI V6 — Security

## Authentication

Three authentication methods, evaluated in priority order:

### 1. API Key (`X-Qarar-API-Key` header)
- Keys configured via `QARAR_API_KEYS_JSON` environment variable
- Each key maps to: `tenant_id`, `subject`, `roles[]`
- Used by: REST API clients, frontend BFF proxy

### 2. OIDC Bearer Token (`Authorization: Bearer <JWT>`)
- Enabled via `OIDC_ENABLED=true`
- Validates against JWKS endpoint (`OIDC_JWKS_URL`)
- Claims extracted: `sub` → subject, `tid` → tenant_id, `roles` → roles
- Supports: Entra ID, Okta, Keycloak, any OIDC-compliant IdP

### 3. MCP Service Key
- Single key via `MCP_API_KEY` environment variable
- Maps to `integration_service` role with `MCP_TENANT_ID`
- Used by: MCP protocol connections (Claude Desktop, ChatGPT, etc.)

## Authorization (RBAC)

| Role | Capabilities |
|------|-------------|
| `admin` | Full access including system configuration |
| `executive` | View cases, approve decisions |
| `project_manager` | Create/analyze cases, upload evidence, submit clarifications |
| `developer` | Technical operations, MCP server management |
| `auditor` | Read-only access to audit trail |
| `integration_service` | MCP tool invocation |

## Tenant Isolation

- `tenant_id` derived from authenticated identity, never from request body/params
- Every database query filters by tenant_id
- Cross-tenant access returns 404 (not 403) to prevent enumeration

## Prompt-Injection Mitigation

- All evidence wrapped in `<untrusted_evidence>` XML tags
- System instructions explicitly tell the model to treat tagged content as data, not commands
- Regex-based flagging for common injection patterns (English + Arabic)
- Suspicious content flagged but not blocked — humans review

## Malware Scanning

- ClamAV integration via `clamd` Python client
- Scans all uploaded files before ingestion
- Infected files quarantined with status `infected`
- When ClamAV unavailable: reports `scan_skipped` (never silently `clean`)

## Rate Limiting

- Sliding-window in-process limiter (swap to Redis for multi-replica)
- Per-user: 120 requests/min general, 20 AI requests/min
- Per-tenant: 600 requests/min
- Daily AI cost budget per tenant (default $25/day)

## Audit Trail

- Append-only `audit_events_v6` table
- No API route may update or delete audit rows
- Events: case_created, case_analyzed, case_clarified, case_approved, automation_executed, evidence_uploaded, mcp_server_registered

## Security Headers

- CORS restricted to configured origins
- Request ID on every response for traceability
- JSON structured logging with OTEL-compatible fields
