# Independent Architecture & Product Review Prompt — Qarar AI V5

Use this prompt unchanged in **Claude Code** and **Codex** so we can compare two independent reviews.

---

You are a principal software architect, staff AI engineer, enterprise security architect, product engineer, and SaaS technical due-diligence reviewer.

Review the entire repository **Qarar AI V5 — Enterprise Decision Intelligence Platform** as if your company were considering:
1. investing in it,
2. deploying it for a Saudi government/enterprise customer,
3. selling it internationally as a commercial SaaS/private-cloud platform.

Do not optimize for politeness. Do not rewrite the whole project immediately. First understand the architecture and run the code/tests that are practical in the environment.

## Product thesis to evaluate
Qarar should be the enterprise evidence-and-decision layer, not another chatbot. It should:
- ingest organizational evidence,
- use official/public research when policy allows,
- invoke only relevant specialist agents,
- produce evidence-traceable recommendations,
- keep humans accountable for decisions,
- expose Qarar through remote MCP to ChatGPT/Claude/Microsoft 365/other MCP hosts,
- consume third-party MCP servers through a gateway,
- automate approved actions through n8n/webhooks,
- maintain separate Executive, Project Manager and Developer/Admin experiences,
- support Arabic/English and RTL/LTR,
- track latency, token usage and cost per case/agent/customer.

## Required review workflow

### Phase 1 — Inventory
Map the repository and identify:
- frontend routes/components,
- backend APIs/models/services,
- decision orchestration flow,
- Knowledge Fabric,
- MCP server,
- MCP client/gateway,
- connector architecture,
- automation architecture,
- persistence/object storage,
- configuration/secrets,
- tests and documentation.

### Phase 2 — Run and verify
Where practical:
- install dependencies,
- run backend tests,
- compile/import Python modules,
- run frontend build/type checks,
- start API and exercise health endpoints,
- exercise create case → analyze,
- test upload → ingestion → retrieval → Q&A,
- start the Qarar MCP server and inspect/list tools,
- test an MCP tool call locally,
- test automation dry-run,
- verify an irrelevant agent is actually skipped,
- verify independent agents do not unnecessarily serialize.

Never claim a test passed unless you ran it.

### Phase 3 — Architecture review
Rate 0–10 and explain:
- product coherence,
- modularity,
- orchestration correctness,
- agent dependency/routing design,
- Knowledge/RAG architecture,
- evidence provenance/citations,
- source trust design,
- MCP server interoperability,
- MCP gateway/client design,
- connector extensibility,
- automation safety,
- security boundaries,
- multi-tenancy readiness,
- scalability,
- observability,
- cost controls,
- testability,
- frontend UX,
- executive UX,
- PM UX,
- developer/admin UX,
- Arabic/English quality,
- commercial readiness.

### Phase 4 — Security threat model
Specifically inspect:
- prompt injection through files/email/web/MCP,
- malicious MCP tools/tool poisoning,
- arbitrary write actions,
- OAuth token handling,
- secret leakage,
- SSRF and remote URL access,
- file upload abuse,
- malware/OCR pipeline risks,
- tenant isolation,
- cross-case evidence leakage,
- authorization gaps,
- audit completeness,
- n8n/webhook misuse,
- cost/denial-of-wallet attacks.

Separate “must fix before any external pilot” from “enterprise hardening later”.

### Phase 5 — Knowledge quality
Check whether Qarar truly uses:
- organization evidence,
- official authoritative sources,
- public/vendor sources,
- LLM knowledge only as interpretation,
with explicit trust/provenance.

Challenge any place where the system could present model knowledge as an authoritative regulatory fact.

### Phase 6 — MCP
Review Qarar in both directions:

A. Qarar as remote MCP server for ChatGPT, Claude, Microsoft 365 agents and other hosts.
B. Qarar as MCP client/gateway consuming GitHub/customer/vendor MCP servers.

Check current official MCP SDK/API compatibility from the installed dependencies or current official docs available to you. Flag stale protocol assumptions.

### Phase 7 — Commercial product review
Answer:
- Is this a sellable category or a feature?
- Who is the best first buyer/persona?
- What is the 5-minute demo story?
- What should be Core vs paid add-ons?
- What should never be exposed to executives?
- Which features create defensibility?
- What is commodity and should use existing standards/tools?
- What are credible pricing dimensions?
- What are the three strongest objections a CIO/CISO/procurement officer will raise?

### Phase 8 — Improvement plan
Produce a prioritized backlog:
- P0 — blocks pilot
- P1 — required for serious customer pilot
- P2 — required for enterprise production
- P3 — scale/market expansion

For every item give:
- problem,
- impact,
- proposed fix,
- affected files/modules,
- estimated complexity S/M/L,
- how to test acceptance.

## Constraints
- Preserve Qarar Core as the product brain.
- Do not turn n8n into the decision engine.
- Do not make ChatGPT or Claude the system of record.
- Prefer MCP/native standards over bespoke connector logic where appropriate.
- Do not run write/destructive external actions without explicit approval.
- Do not hide incomplete features behind misleading “connected/complete” UI.
- Do not put raw agent internals in the Executive experience.
- Avoid blanket rewrites unless the architecture truly requires one.

## Deliverable
Return one report with:
1. Executive verdict (max 10 lines)
2. Scorecard
3. What is genuinely strong
4. What is not yet credible
5. Bugs/test failures actually observed
6. Security findings
7. MCP assessment
8. Knowledge/RAG assessment
9. UX/product assessment
10. Commercial positioning assessment
11. Prioritized P0–P3 backlog
12. Recommended V5.1 architecture changes
13. Go / No-Go recommendation for:
   - internal demo,
   - design-partner pilot,
   - government pilot,
   - production enterprise sale.

Be specific, evidence-based and reference file paths/functions. If you did not verify something, explicitly label it “not verified”.
