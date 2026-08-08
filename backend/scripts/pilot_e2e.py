"""End-to-end pilot scenario — exercises the full V6 lifecycle via REST API."""
import sys, os, json, time, httpx
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = "http://localhost:8000/api"
PM_KEY = "qarar-local-dev-key-change-me"   # all roles for local-dev tenant
EXEC_KEY = "readonly-key"  # executive role for local-dev tenant

def h(key): return {"X-Qarar-API-Key": key, "Content-Type": "application/json"}

def step(n, desc):
    print(f"\n{'='*60}\nSTEP {n}: {desc}\n{'='*60}")

def main():
    c = httpx.Client(timeout=30)

    # Step 1: Health check
    step(1, "Health check")
    r = c.get(f"{BASE}/health", headers=h(PM_KEY))
    assert r.status_code == 200
    print(json.dumps(r.json(), indent=2))

    # Step 2: Readiness probe
    step(2, "Readiness probe")
    r = c.get(f"{BASE}/readyz")
    assert r.status_code == 200
    print(json.dumps(r.json(), indent=2))

    # Step 3: Who am I?
    step(3, "Who am I? (PM key)")
    r = c.get(f"{BASE}/whoami", headers=h(PM_KEY))
    assert r.status_code == 200
    who = r.json()
    print(json.dumps(who, indent=2))
    assert who["tenant_id"] == "local-dev"

    # Step 4: Create a new decision case
    step(4, "Create decision case")
    r = c.post(f"{BASE}/cases", headers=h(PM_KEY), json={
        "title": "ترحيل البريد الإلكتروني إلى Microsoft 365 أم Google Workspace",
        "description": "الوزارة تدرس ترحيل البريد الإلكتروني من الخوادم المحلية إلى سحابة. الخيارات المتاحة: Microsoft 365 وGoogle Workspace والبقاء محليًا. يجب تقييم الأمن والتكلفة والتوافق مع أنظمة هيئة الاتصالات.",
        "urgency": "high",
        "category": "technology",
        "language": "ar"
    })
    assert r.status_code == 201
    case = r.json()
    cid = case["id"]
    print(f"Case created: id={cid}, status={case['status']}")

    # Step 5: Upload evidence
    step(5, "Upload evidence document")
    r = c.post(f"{BASE}/fabric/upload", headers={"X-Qarar-API-Key": PM_KEY},
               files={"file": ("policy.txt", b"Government cloud hosting policy: all email must use Saudi-hosted or certified international providers with data residency in KSA.", "text/plain")},
               data={"trust_level": "A", "case_id": str(cid)})
    assert r.status_code == 200
    print(f"Upload: {r.json()}")

    # Step 6: Analyze
    step(6, "Analyze case (mock AI)")
    r = c.post(f"{BASE}/cases/{cid}/analyze", headers=h(PM_KEY))
    assert r.status_code == 200
    case = r.json()
    print(f"Status after analysis: {case['status']}")
    print(f"Selected agents: {case['selected_agents']}")
    print(f"Skipped agents: {case['skipped_agents']}")
    print(f"Analysis source: {case['analysis_source']}")

    # Step 7: Check if clarification needed
    step(7, "Check clarification gate")
    if case["status"] == "needs_clarification":
        print(f"Questions: {case['pending_clarifications']}")
        # Answer the questions
        r = c.post(f"{BASE}/cases/{cid}/clarify", headers=h(PM_KEY), json={
            "answers": {q: f"Answer to: {q}" for q in (case["pending_clarifications"] or [])}
        })
        assert r.status_code == 200
        case = r.json()
        print(f"After clarification: status={case['status']}")
    else:
        print(f"No clarification needed, status={case['status']}")

    # Step 8: List cases
    step(8, "List all cases")
    r = c.get(f"{BASE}/cases", headers=h(PM_KEY))
    assert r.status_code == 200
    cases = r.json()
    print(f"Total cases: {len(cases)}")

    # Step 9: Get single case
    step(9, "Get case detail")
    r = c.get(f"{BASE}/cases/{cid}", headers=h(PM_KEY))
    assert r.status_code == 200
    print(f"Case {cid}: {r.json()['title']}, status={r.json()['status']}")

    # Step 10: Fabric — ask a question
    step(10, "Knowledge Fabric — ask a question")
    r = c.post(f"{BASE}/fabric/ask", headers=h(PM_KEY), json={
        "question": "ما هي سياسة الاستضافة السحابية الحكومية؟",
        "language": "ar",
        "mode": "official_plus_organization",
        "case_id": cid
    })
    assert r.status_code == 200
    ans = r.json()
    print(f"Answer length: {len(ans.get('answer',''))}")
    print(f"Sources: {len(ans.get('sources', []))}")

    # Step 11: Tenant isolation — tenant-b cannot see local-dev's case
    step(11, "Tenant isolation check")
    r = c.get(f"{BASE}/cases/{cid}", headers=h("tenant-b-key"))
    assert r.status_code == 404
    print("PASS: tenant-b cannot access tenant-a's case")

    # Step 12: Approve the decision (executive role)
    step(12, "Executive approval")
    # First ensure case has analysis with options
    r = c.get(f"{BASE}/cases/{cid}", headers=h(PM_KEY))
    case = r.json()
    options = (case.get("analysis") or {}).get("options", [])
    if options:
        oid = options[0]["id"]
        r = c.post(f"{BASE}/cases/{cid}/approve", headers=h(EXEC_KEY), json={
            "option_id": oid,
            "decision_owner": "Dr. Ahmed Al-Rashid",
            "due_date": "2026-09-15"
        })
        assert r.status_code == 200
        case = r.json()
        print(f"Approved: option={case['approved_option']}, owner={case['decision_owner']}, status={case['status']}")
    else:
        print("SKIP: mock AI did not produce options (expected in AI_ENABLED=false)")

    # Step 13: Automation dry run
    step(13, "Automation dry run")
    r = c.post(f"{BASE}/connect/automation/run", headers=h(PM_KEY), json={
        "workflow_id": "decision_to_action",
        "payload": {"case_id": cid, "note": "Pilot E2E test"},
        "dry_run": True
    })
    assert r.status_code == 200
    print(f"Dry run result: {r.json()['status']}")

    # Step 14: Connect catalog
    step(14, "Connect catalog")
    r = c.get(f"{BASE}/connect/catalog", headers=h(PM_KEY))
    assert r.status_code == 200
    cat = r.json()
    print(f"Connectors: {len(cat.get('connectors', []))}")
    print(f"MCP servers: {len(cat.get('mcp_servers', []))}")
    print(f"Automations: {len(cat.get('automations', []))}")

    # Step 15: Readiness probe (unauthenticated)
    step(15, "Readyz is publicly accessible")
    r = c.get(f"{BASE}/readyz")
    assert r.status_code == 200
    print(f"System: {r.json()['status']}")

    # Step 16: Unauthenticated access blocked
    step(16, "Unauthenticated access blocked")
    r = c.get(f"{BASE}/cases")
    assert r.status_code in (401, 403)
    print(f"PASS: unauthenticated request rejected with {r.status_code}")

    print(f"\n{'='*60}")
    print("PILOT SCENARIO COMPLETE — ALL STEPS PASSED")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
