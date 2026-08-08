# Qarar AI V6 — MCP (Model Context Protocol)

## Qarar as MCP Server

Qarar exposes 15 tools via MCP Streamable HTTP transport on port 8001.

### Tools

| Tool | Description | Role Gate |
|------|------------|-----------|
| `health` | Server health check | Any |
| `ask_qarar` | Knowledge Fabric Q&A | Any |
| `search_evidence` | Search knowledge chunks | Any |
| `add_evidence` | Upload text evidence | PM, Developer |
| `create_case` | Create new decision case | PM, Developer |
| `get_case` | Get case details | Any |
| `list_cases` | List tenant's cases | Any |
| `get_case_status` | Quick status check | Any |
| `get_executive_brief` | Executive summary | Executive |
| `get_decision` | Full decision analysis | Any |
| `get_risks` | Risk analysis extract | Any |
| `run_decision_council` | Trigger full analysis | PM, Developer |
| `approve_decision` | Executive approval | Executive |
| `execute_approved_workflow` | Trigger automation | PM, Developer |

### Authentication

MCP connections authenticate via `MCP_API_KEY` environment variable, passed as a bearer token. The gateway creates an `httpx.AsyncClient(headers=...)` and passes it as the `http_client=` parameter to `streamable_http_client()`.

### Configuration

```bash
# Start MCP server
python -m uvicorn app.mcp_server:app --host 0.0.0.0 --port 8001
```

## Qarar as MCP Client (Gateway)

The MCP gateway connects to remote MCP servers to extend Qarar's capabilities.

### System Servers

Configured in `backend/config/mcp_servers.json`:

```json
[
  {
    "id": "internal-tools",
    "name": "Internal Tools",
    "url": "https://mcp.example.com/sse",
    "api_key_env": "INTERNAL_MCP_KEY",
    "enabled": true,
    "tool_allowlist": ["search", "lookup"]
  }
]
```

### Tenant-Owned Servers

Tenants can register their own MCP servers via the REST API:

```bash
# Register
POST /api/connect/mcp/servers
{"name": "my-server", "url": "https://...", "api_key": "..."}

# Health check
POST /api/connect/mcp/{id}/health

# Toggle enable/disable
PATCH /api/connect/mcp/servers/{id}
{"enabled": false}

# Delete
DELETE /api/connect/mcp/servers/{id}
```

### Tool Allowlists

Both system and tenant servers support tool allowlists. If set, only listed tools can be called through the gateway.
