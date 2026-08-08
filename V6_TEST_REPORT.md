# Qarar AI V6 — Test Report

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 45 |
| Passed | 45 |
| Failed | 0 |
| Duration | ~10 seconds |
| Framework | pytest 8.4.1 |
| Python | 3.13.14 |

## Test Breakdown

### V5.1 Baseline Tests (24 tests — all pass)

| Test | File | Purpose |
|------|------|---------|
| `test_100_planner_runs` | test_100_plans.py | 100 random cases through planner |
| `test_create_analyze_roundtrip` | test_api_e2e.py | Create + analyze lifecycle |
| `test_live_stream_emits_plan_agents_and_complete` | test_api_e2e.py | SSE streaming events |
| `test_text_upload_extract` | test_knowledge.py | File upload + text extraction |
| `test_relevance` | test_knowledge.py | Knowledge retrieval relevance |
| `test_mcp_anonymous_rejected` | test_mcp_auth_middleware.py | MCP auth enforcement |
| `test_mcp_authenticated_allowed_and_context_set` | test_mcp_auth_middleware.py | MCP auth success |
| `test_unauthenticated_api_is_rejected` | test_security_v51.py | Auth requirement |
| `test_whoami` | test_security_v51.py | Identity endpoint |
| `test_tenant_case_isolation` | test_security_v51.py | Cross-tenant blocked |
| `test_role_gate_blocks_analysis_for_read_only_role` | test_security_v51.py | RBAC enforcement |
| `test_non_dry_automation_requires_server_verified_approval` | test_security_v51.py | Approval gate |
| `test_client_supplied_approved_flag_no_longer_exists` | test_security_v51.py | V5 bypass closed |
| `test_fabric_is_tenant_scoped_and_upload_cannot_self_assert_trust_a` | test_security_v51.py | Trust A protection |
| `test_approval_record_allows_execution_gate_then_n8n_is_attempted` | test_security_v51.py | Full approval flow |
| `test_simple_skips_cloud` | test_specific_plans.py | Planner routing |
| `test_cloud_selects_cloud_data_cyber` | test_specific_plans.py | Planner routing |
| `test_vendor_selects_legal_procurement` | test_specific_plans.py | Planner routing |
| `test_connector_catalog_has_mcp_and_n8n` | test_v5_connect.py | Connector catalog |
| `test_mcp_config_loads` | test_v5_connect.py | MCP config loading |
| `test_chunking_large_text` | test_v5_fabric.py | Text chunking |
| `test_lexical` | test_v5_fabric.py | Lexical search |
| `test_automation_defaults_to_dry_run` | test_v5_fabric.py | Dry-run default |
| `test_research_modes_present` | test_v5_fabric.py | Research mode config |

### V6 Platform Tests (18 tests — all pass)

| Test | Purpose |
|------|---------|
| `test_dry_run_blocked_for_wrong_tenant_case` | Tenant isolation on dry-run |
| `test_dry_run_allowed_for_own_tenant_case` | Own-tenant dry-run allowed |
| `test_rate_limit_blocks_after_threshold` | Rate limiting enforcement |
| `test_oidc_disabled_by_default_rejects_bearer_token` | OIDC off → reject |
| `test_oidc_validates_locally_signed_jwt` | Full OIDC flow with RSA |
| `test_oidc_rejects_wrong_audience` | JWT audience validation |
| `test_flags_suspicious_instruction_override_attempt` | English prompt injection |
| `test_clean_evidence_is_not_flagged` | Clean text not flagged |
| `test_wrap_untrusted_content_frames_data_not_instruction` | XML framing works |
| `test_malware_scan_disabled_reports_scan_skipped` | Scan disabled → scan_skipped |
| `test_clarify_endpoint_stores_answers_and_unblocks` | Clarification gate lifecycle |
| `test_clarify_empty_answers_rejected` | Empty answers → 400 |
| `test_approve_requires_executive_role` | Approval without analysis → 404 |
| `test_approve_with_valid_option` | Valid approval flow |
| `test_approve_invalid_option_rejected` | Invalid option → 400 |
| `test_audit_events_recorded_on_case_create` | Audit trail on create |
| `test_readyz_returns_ok` | Readiness probe |
| `test_flags_arabic_prompt_injection` | Arabic prompt injection |

### V6 MCP Gateway Integration Tests (3 tests — all pass)

| Test | Purpose |
|------|---------|
| `test_gateway_unauthorized_connection_fails` | Unauthenticated MCP blocked |
| `test_gateway_authenticated_list_tools_and_call_health` | Authenticated MCP flow |
| `test_gateway_health_test_records_status` | Health status persisted |

## E2E Pilot Scenario (16 steps — all pass)

Executed via `scripts/pilot_e2e.py` against a live server:

| Step | Action | Result |
|------|--------|--------|
| 1 | Health check | 200, version 6.0.0 |
| 2 | Readiness probe | 200, status ready |
| 3 | Who am I | Correct tenant + roles |
| 4 | Create case | 201, case created |
| 5 | Upload evidence | 200, Trust B assigned |
| 6 | Analyze | 200, 5 agents selected |
| 7 | Clarification gate | Triggered, 3 questions |
| 8 | Clarify answers | 200, recommendation_ready |
| 9 | List cases | Correct count |
| 10 | Get case detail | Correct data |
| 11 | Knowledge Q&A | Answer with sources |
| 12 | Tenant isolation | 404 cross-tenant |
| 13 | Executive approval | Option B approved |
| 14 | Automation dry run | dry_run status |
| 15 | Readyz public | 200 |
| 16 | Unauth blocked | 401 |

## Frontend Build

```
Next.js build: 17 pages, 0 errors
  ○ Static: 12 pages
  ƒ Dynamic: 5 pages
  First Load JS: 103 kB shared
```
