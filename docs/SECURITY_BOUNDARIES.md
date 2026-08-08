# Security boundaries

This reference implementation is not a substitute for production identity/governance. Before external deployment add OAuth/SSO, RBAC, tenant isolation enforcement, secret manager/KMS, malware scanning, egress allowlists, MCP tool allowlists, write-action approval, audit retention, rate/cost limits, and production observability. Treat file/email/web/MCP content as untrusted and prompt-injection capable.
