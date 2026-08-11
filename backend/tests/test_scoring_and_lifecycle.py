import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.tools.scoring import compose_confidence, normalize_weights, score_options

client = TestClient(app)
HEADERS = {'X-Qarar-API-Key': 'key-a'}


def test_weights_are_normalized_and_unknown_criteria_rejected():
    assert normalize_weights({'risk': 2, 'financial': 1}) == {'risk': 0.666667, 'financial': 0.333333}
    with pytest.raises(ValueError, match='Unknown scoring criterion'):
        normalize_weights({'popularity': 1})


def test_missing_scores_are_explicit_not_silently_zeroed():
    result = score_options([{'id': 'A', 'criterion_scores': {'risk': 80}}], {'risk': 1, 'financial': 1})[0]
    assert result['weighted_score'] is None
    assert result['score_valid'] is False
    assert result['missing_criteria'] == ['financial']
    assert result['score_completeness'] == .5


def test_confidence_is_deterministic_and_explained():
    options = score_options([
        {'id': 'A', 'criterion_scores': {'risk': 80}},
        {'id': 'B', 'criterion_scores': {'risk': 60}},
    ], {'risk': 1})
    value, breakdown = compose_confidence(
        {'facts': ['fact'], 'missing_information': [], 'sources': [{'id': 1}]}, options,
    )
    assert value == .9
    assert breakdown['method'] == 'deterministic-v1'
    assert breakdown['uncalibrated_model_confidence_excluded'] is True


def test_case_custom_scoring_edit_and_audited_lifecycle():
    created = client.post('/api/cases', headers=HEADERS, json={
        'title': 'Custom scoring decision',
        'description': 'Choose an option with explicit custom financial and risk criteria.',
        'scoring_weights': {'risk': 2, 'financial': 1},
    })
    assert created.status_code == 201
    case = created.json()
    assert case['scoring_weights'] == {'risk': 0.666667, 'financial': 0.333333}

    updated = client.patch(f"/api/cases/{case['id']}", headers=HEADERS, json={'urgency': 'high'})
    assert updated.status_code == 200
    assert updated.json()['urgency'] == 'high'

    deferred = client.post(f"/api/cases/{case['id']}/transition", headers=HEADERS,
                           json={'status': 'deferred', 'reason': 'Waiting for validated financial evidence'})
    assert deferred.status_code == 200
    assert deferred.json()['status'] == 'deferred'

    reopened = client.post(f"/api/cases/{case['id']}/transition", headers=HEADERS,
                           json={'status': 'open', 'reason': 'Evidence received; resume analysis'})
    assert reopened.status_code == 200
    assert reopened.json()['status'] == 'open'


def test_case_rejects_invalid_scoring_configuration():
    response = client.post('/api/cases', headers=HEADERS, json={
        'title': 'Invalid scoring decision',
        'description': 'This request intentionally includes an unsupported criterion.',
        'scoring_weights': {'popularity': 1},
    })
    assert response.status_code == 422
