# Qarar AI V6 — Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION TIER                       │
│  Next.js 15.5 BFF (Browser → Server Routes → Backend API)  │
│  Three experiences: Executive | PM | Developer              │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────────┐
│                      APPLICATION TIER                       │
│  FastAPI REST API (port 8000)                               │
│  ┌─────────────┬──────────────┬─────────────────────────┐  │
│  │ Cases API   │ Fabric API   │ Connect API             │  │
│  │ CRUD+Analyze│ Upload+Ask   │ MCP Registry+Automation │  │
│  └──────┬──────┴──────┬───────┴──────────┬──────────────┘  │
│         │             │                  │                  │
│  ┌──────▼──────┐ ┌────▼─────┐  ┌─────────▼──────────┐     │
│  │ Orchestrator│ │ Knowledge│  │ MCP Gateway         │     │
│  │ Planner     │ │ Fabric   │  │ (client to remotes) │     │
│  │ 18 Agents   │ │ pgvector │  │ + Registry CRUD     │     │
│  └─────────────┘ │ hybrid   │  └─────────────────────┘     │
│                  │ search   │                               │
│  MCP Server ─────┤          │  Automation Engine            │
│  (15 tools)      └──────────┘  n8n webhooks + callbacks     │
│                                                             │
│  Cross-cutting: Auth │ Audit │ RateLimit │ MalwareScan      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                        DATA TIER                            │
│  PostgreSQL 16 + pgvector (IVFFlat)                         │
│  12 tables across 4 model modules                           │
│  Alembic migrations │ Object storage (local/S3)             │
└─────────────────────────────────────────────────────────────┘
```

## Decision Lifecycle

1. **Case creation** — PM submits title + description + urgency + category
2. **Evidence ingestion** — files uploaded → malware scanned → chunked → embedded → indexed in pgvector
3. **Analysis** — Planner selects agents → parallel execution → scoring → synthesis
4. **Clarification gate** — unknowns classified → auto-retrievable resolved → human questions surfaced
5. **Recommendation** — executive brief with confidence, options, risks, next actions
6. **Approval** — executive selects option → immutable DecisionApproval record created
7. **Execution** — automation engine sends webhook → n8n processes → callback confirms

## Database Schema (12 tables)

| Table | Purpose |
|-------|---------|
| `decision_cases` | Core decision cases with full analysis results |
| `knowledge_sources_v5` | Uploaded evidence with trust levels A/B/C/D |
| `knowledge_chunks_v5` | Chunked text for retrieval |
| `knowledge_chunk_vectors_v6` | pgvector embeddings (IVFFlat index) |
| `automation_runs_v5` | Automation execution records with callback status |
| `decision_approvals_v51` | Immutable approval records |
| `audit_events_v6` | Append-only audit trail |
| `usage_records_v6` | AI usage ledger with actual vs estimated costs |
| `cost_budgets_v6` | Per-tenant daily budget configuration |
| `mcp_server_registrations_v6` | Tenant-owned remote MCP server registry |
| `scan_results_v6` | Malware scan outcomes per uploaded source |

## Tenant Isolation

Every query includes `tenant_id` derived from the authenticated principal — never client-supplied.

## Trust Levels

| Level | Source | Policy |
|-------|--------|--------|
| A | Government gazette, official regulation | Governance-verified only |
| B | Organizational evidence, PM clarifications | Default for uploads |
| C | Public sources, vendor material | Allowed |
| D | Unverified, user-generated | Flagged in citations |
