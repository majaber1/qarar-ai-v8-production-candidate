from fastapi.testclient import TestClient
from app.main import app
from app.services.tools.scoring import (
    score_options, sensitivity_analysis, evaluate_business_scenarios,
    DECISION_TEMPLATES, SCENARIO_PRESETS
)

client = TestClient(app)
AUTH_PM = {'X-Qarar-API-Key': 'key-a'}
AUTH_DEV = {'X-Qarar-API-Key': 'key-a'}
AUTH_OTHER = {'X-Qarar-API-Key': 'key-b'}

def test_generic_decision_templates_endpoint():
    resp = client.get('/api/cases/templates', headers=AUTH_PM)
    assert resp.status_code == 200, resp.text
    templates = resp.json()
    assert len(templates) == 5
    template_ids = {t['id'] for t in templates}
    expected_ids = {
        'cloud_platform_selection',
        'cybersecurity_mdr_selection',
        'tender_contractor_award',
        'regional_expansion',
        'ai_portfolio_prioritization'
    }
    assert template_ids == expected_ids
    for t in templates:
        assert 'criteria' in t and len(t['criteria']) >= 4
        assert 'default_options' in t and len(t['default_options']) >= 3
        assert 'clarification_questions' in t and len(t['clarification_questions']) >= 2

def test_scenario_presets_endpoint():
    resp = client.get('/api/cases/scenarios/presets', headers=AUTH_PM)
    assert resp.status_code == 200, resp.text
    presets = resp.json()
    assert len(presets) == 5
    preset_ids = [p['id'] for p in presets]
    assert preset_ids == ['balanced', 'risk_compliance', 'cost', 'speed', 'strategic_growth']

def test_explicit_user_defined_options_and_provenance():
    # Create case with explicit user-defined options (Azure, AWS, GCP)
    payload = {
        'title': 'Enterprise Cloud Platform Selection - KSA Region',
        'description': 'Select cloud provider compliant with national cybersecurity ECC and sovereign data hosting.',
        'scoring_criteria': [
            {'key': 'compliance', 'name': 'الامتثال والسيادة الرقمية', 'weight': 0.35, 'is_gate': True, 'gate_min': 80.0},
            {'key': 'security', 'name': 'الأمان والتشفير', 'weight': 0.25},
            {'key': 'financial', 'name': 'التكلفة الإجمالية TCO', 'weight': 0.25},
            {'key': 'time', 'name': 'سرعة وجاهزية النقل', 'weight': 0.15},
        ],
        'options': [
            {
                'id': 'azure',
                'title': 'Microsoft Azure (KSA)',
                'description': 'Local sovereign region with CCC compliance.',
                'criterion_scores': {'compliance': 95.0, 'security': 90.0, 'financial': 75.0, 'time': 85.0},
                'criterion_provenance': {
                    'compliance': {
                        'rationale': 'حاصل على شهادة ترخيص CCC من هيئة الاتصالات والفضاء والتقنية ومراكز بيانات بالرياض وجدة.',
                        'evidence_references': ['شهادة ترخيص الحوسبة السحابية CCC-2025', 'تقرير تدقيق الامتثال للضوابط ECC-1:2018'],
                        'source_ids': [101, 102],
                        'trust_level': 'A',
                        'confidence': 0.98,
                    }
                }
            },
            {
                'id': 'aws',
                'title': 'AWS (Sovereign Outposts)',
                'description': 'Dedicated sovereign outposts and IAM governance.',
                'criterion_scores': {'compliance': 88.0, 'security': 92.0, 'financial': 80.0, 'time': 70.0},
            },
            {
                'id': 'gcp',
                'title': 'Google Cloud Platform (Dammam)',
                'description': 'Advanced AI analytics with Dammam data center.',
                'criterion_scores': {'compliance': 72.0, 'security': 85.0, 'financial': 88.0, 'time': 78.0},
            }
        ]
    }
    created = client.post('/api/cases', headers=AUTH_PM, json=payload)
    assert created.status_code == 201, created.text
    case = created.json()
    case_id = case['id']
    assert len(case['options']) == 3
    assert case['options'][0]['id'] == 'azure'

    # Run analysis
    analyzed = client.post(f'/api/cases/{case_id}/analyze', headers=AUTH_PM)
    assert analyzed.status_code == 200, analyzed.text
    result = analyzed.json()
    
    # Verify user options were preserved, not replaced with generic A/B/C
    options = result['analysis']['options']
    assert len(options) == 3
    opt_ids = {o['id'] for o in options}
    assert opt_ids == {'azure', 'aws', 'gcp'}

    # Verify Mandatory Gate: GCP failed compliance gate (72 < 80)
    gcp_opt = next(o for o in options if o['id'] == 'gcp')
    assert gcp_opt['is_disqualified'] is True
    assert gcp_opt['status'] == 'disqualified'
    assert len(gcp_opt['gate_failures']) == 1
    assert gcp_opt['gate_failures'][0]['criterion_key'] == 'compliance'
    # Disqualified option still retains numeric score for audit
    assert gcp_opt['weighted_score'] is not None

    # Azure must be the recommended leader (Azure: 95*0.35 + 90*0.25 + 75*0.25 + 85*0.15 = 87.25)
    azure_opt = next(o for o in options if o['id'] == 'azure')
    assert azure_opt['is_disqualified'] is False
    assert azure_opt['rank'] == 1
    assert azure_opt['weighted_score'] == 87.25
    assert result['analysis']['executive']['recommended_option_id'] == 'azure'

    # Acceptance Test: "Why is Azure Compliance 95 instead of 88?"
    # Query granular score provenance endpoint
    prov_resp = client.get(f'/api/cases/{case_id}/provenance/azure/compliance', headers=AUTH_PM)
    assert prov_resp.status_code == 200, prov_resp.text
    prov = prov_resp.json()
    assert prov['criterion_key'] == 'compliance'
    assert prov['raw_score'] == 95.0
    assert prov['normalized_score'] == 95.0
    assert prov['weighted_contribution'] == 33.25  # 95 * 0.35
    assert prov['trust_level'] == 'A'
    assert 'CCC-2025' in prov['evidence_references'][0]
    assert prov['assessment_method'] == 'deterministic-provenance-v9'

    # Verify Business Scenarios Presets are present in analysis
    scenarios = result['analysis']['scenarios']
    assert len(scenarios) == 5
    assert {s['preset_id'] for s in scenarios} == {'balanced', 'risk_compliance', 'cost', 'speed', 'strategic_growth'}

    # Human Review & Score Override Test:
    # An authorized reviewer overrides Azure financial score from 75 to 90 with mandatory reason
    override_payload = {
        'option_id': 'azure',
        'criterion_key': 'financial',
        'new_score': 90.0,
        'reason': 'Special enterprise government discount discount applied (-15% TCO).'
    }
    override_resp = client.post(f'/api/cases/{case_id}/override', headers=AUTH_PM, json=override_payload)
    assert override_resp.status_code == 200, override_resp.text
    updated_case = override_resp.json()
    
    # Verify override history recorded
    assert len(updated_case['override_history']) == 1
    ov_hist = updated_case['override_history'][0]
    assert ov_hist['option_id'] == 'azure'
    assert ov_hist['criterion_key'] == 'financial'
    assert ov_hist['previous_score'] == 75.0
    assert ov_hist['new_score'] == 90.0
    assert 'Special enterprise government discount' in ov_hist['reason']

    # Verify Azure financial recalculated (Azure: 95*0.35 + 90*0.25 + 90*0.25 + 85*0.15 = 91.00)
    updated_azure = next(o for o in updated_case['analysis']['options'] if o['id'] == 'azure')
    assert updated_azure['weighted_score'] == 91.0

    # Verify provenance endpoint reflects the override
    fin_prov = client.get(f'/api/cases/{case_id}/provenance/azure/financial', headers=AUTH_PM).json()
    assert fin_prov['raw_score'] == 90.0
    assert fin_prov['assessment_source'] == 'HUMAN'
    assert len(fin_prov['override_history']) == 1

def test_override_stale_recommendation_trigger():
    # Create case where Option B leads, then override Option A to surpass Option B
    payload = {
        'title': 'MDR Vendor Selection',
        'description': 'Evaluate managed detection and response providers.',
        'scoring_criteria': [
            {'key': 'quality', 'name': 'Quality', 'weight': 0.5},
            {'key': 'cost', 'name': 'Cost', 'weight': 0.5},
        ],
        'options': [
            {'id': 'vendor_a', 'title': 'Vendor A', 'criterion_scores': {'quality': 70.0, 'cost': 70.0}},
            {'id': 'vendor_b', 'title': 'Vendor B', 'criterion_scores': {'quality': 80.0, 'cost': 80.0}},
        ]
    }
    case = client.post('/api/cases', headers=AUTH_PM, json=payload).json()
    case_id = case['id']
    
    analyzed = client.post(f'/api/cases/{case_id}/analyze', headers=AUTH_PM).json()
    assert analyzed['analysis']['executive']['recommended_option_id'] == 'vendor_b'
    
    # Override vendor_a quality to 98.0 -> makes vendor_a score (98+70)/2 = 84.0 > vendor_b (80.0)
    override = client.post(f'/api/cases/{case_id}/override', headers=AUTH_PM, json={
        'option_id': 'vendor_a',
        'criterion_key': 'quality',
        'new_score': 98.0,
        'reason': 'Validated Tier-4 SOC certification with sub-5-minute SLA.'
    }).json()
    
    assert override['analysis']['executive']['recommended_option_id'] == 'vendor_a'
    assert override['analysis']['executive'].get('recommendation_stale') is True
    assert 'stale_reason' in override['analysis']['executive']

def test_tenant_isolation_on_new_endpoints():
    payload = {
        'title': 'Tenant A Private Case',
        'description': 'Sensitive procurement case for tenant A.',
        'scoring_criteria': [{'key': 'fit', 'name': 'Fit', 'weight': 1.0}],
        'options': [{'id': 'opt1', 'title': 'Opt 1', 'criterion_scores': {'fit': 90.0}}]
    }
    case_a = client.post('/api/cases', headers=AUTH_PM, json=payload).json()
    case_id = case_a['id']
    client.post(f'/api/cases/{case_id}/analyze', headers=AUTH_PM)

    # Tenant B tries to access provenance -> 404
    resp = client.get(f'/api/cases/{case_id}/provenance/opt1/fit', headers=AUTH_OTHER)
    assert resp.status_code == 404

    # Tenant B tries to override score -> 404
    override_resp = client.post(f'/api/cases/{case_id}/override', headers=AUTH_OTHER, json={
        'option_id': 'opt1', 'criterion_key': 'fit', 'new_score': 50.0, 'reason': 'Malicious override'
    })
    assert override_resp.status_code == 404
