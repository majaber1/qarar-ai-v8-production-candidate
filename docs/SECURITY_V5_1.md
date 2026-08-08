# Qarar V5.1 Security Model

## Trust boundaries

1. **Browser boundary** — browser talks to the Next.js BFF, not directly to the backend secret.
2. **REST boundary** — authenticated principal required for business APIs.
3. **MCP boundary** — authenticated before MCP protocol/tool dispatch.
4. **Tenant boundary** — tenant comes from identity, never from a request parameter.
5. **Approval boundary** — execution authorization comes from a persisted server record, never a client boolean.
6. **Knowledge boundary** — ordinary uploads cannot mark themselves authoritative Trust A.

## Reference identity

API keys are a replaceable pilot identity provider. Production OIDC should produce the same internal Principal contract.

## Known remaining gaps

- no malware scanner yet
- no durable rate-limit backend yet
- no production secrets manager yet
- no OIDC implementation yet
- no vector DB/ANN yet
- no durable background worker yet

These are intentionally P1/P2 items rather than hidden assumptions.
