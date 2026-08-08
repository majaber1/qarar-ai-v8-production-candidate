# Qarar AI V6.0 — Release Notes

## What's New

### Enterprise Infrastructure
- **PostgreSQL + pgvector** replaces SQLite for production workloads
- **Alembic migrations** for reproducible schema management
- **OIDC/SSO** scaffold with JWT/JWKS validation (Entra ID, Okta, Keycloak ready)
- **ClamAV malware scanning** for uploaded evidence
- **Docker Compose** with PostgreSQL, pgvector, ClamAV, n8n profiles

### Decision Intelligence
- **Intelligent clarification gate** — auto-classifies unknowns into auto-retrievable, inferable, and human-required; surfaces only critical questions to the PM
- **18 domain agents** with Arabic skip reasons explaining WHY each was excluded
- **Knowledge Fabric** — pgvector hybrid retrieval (ANN + full-text), XLSX/PPTX support
- **Executive approval flow** — immutable DecisionApproval records with option/owner/due-date

### Security & Governance
- **Prompt-injection mitigation** — `<untrusted_evidence>` XML framing + regex flagging (EN+AR)
- **Rate limiting** — sliding-window per-user (120/min), per-tenant (600/min), AI-specific (20/min)
- **Cost governance** — daily AI budget per tenant ($25 default)
- **Audit trail** — append-only events covering create → analyze → clarify → approve → execute

### MCP (Model Context Protocol)
- **15 MCP server tools** (expanded from 5) with role gates and budget checks
- **MCP gateway registry** — tenants can register, health-check, and manage remote MCP servers
- **Tool allowlists** on both system and tenant-owned servers
- **Fixed**: `streamable_http_client()` auth via `http_client=` parameter (MCP SDK 2.0.0)

### Automation
- **Real n8n integration** — webhook outbound + callback inbound
- **Tenant-verified callbacks** — `qarar_run_id` + `tenant_id` verification
- **Race condition fix** — callback during POST no longer clobbered

### Frontend
- **Premium design** — Inter + IBM Plex Sans Arabic, emerald/gold/ivory palette
- **Executive Decision Cockpit** — live stats, approval flow, approved banner
- **PM Workspace** — clarification gate UI, evidence gaps, specialist cards
- **Developer AI Ops** — system health dashboard, execution audit, provider metrics
- **MCP Server Registry** — CRUD UI with health checks and enable/disable
- **Package bumped** to v6.0.0

### Testing
- **45 automated tests** (24 baseline + 18 V6 platform + 3 MCP gateway integration)
- **16-step E2E pilot** exercising the full decision lifecycle
- **Demo seed script** with 4 Arabic/English cases and evidence

## Breaking Changes

- PostgreSQL recommended for production (SQLite still works for development)
- `CaseResponse` schema now includes `pending_clarifications` and `clarification_answers`
- MCP server expanded from 5 → 15 tools (additive, backward compatible)
- Docker Compose now includes PostgreSQL as default database

## Migration from V5.1

1. Set `DATABASE_URL` to PostgreSQL connection string
2. Run `python -m alembic upgrade head`
3. Update frontend package: `npm install`
4. No API breaking changes — all V5.1 endpoints remain compatible
