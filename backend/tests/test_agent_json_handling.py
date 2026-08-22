"""Regression tests for base.BaseAgent.ask_json() non-dict JSON handling.

Covers the confirmed production defect: the LLM occasionally returns valid JSON
that is not an object (a bare string, list, number, etc.), which previously
crashed mk() with AttributeError and was silently swallowed into a mock
fallback. ask_json() must now retry once with a corrective instruction, and
only surface a clear failure (never a fabricated success) if the retry also
fails to produce a JSON object.
"""
import app.services.agents.base as base_module
from app.services.agents.base import BaseAgent
from app.services.agents.risk import RiskAgent
from app.services.contracts import CaseInput, ExecutionContext


class DummyAgent(BaseAgent):
    name = 'dummy'

    def execute(self, ctx):
        data, usage = self.ask_json(ctx, 'instructions', {'x': 1})
        return self.mk(data, metadata={'usage': usage})


def _usage(tokens=10):
    return {'input_tokens': tokens, 'output_tokens': tokens, 'total_tokens': tokens * 2, 'estimated_cost_usd': 0.001}


def _make_fake_llm_client(responses):
    """responses: list of (raw_text, usage_dict) tuples, consumed in call order."""
    calls = []

    class FakeLLMClient:
        def __init__(self):
            pass

        def generate_with_meta(self, instructions, payload):
            calls.append(instructions)
            return responses.pop(0)

    return FakeLLMClient, calls


def _ctx():
    case = CaseInput(case_id=1, title='t', description='d', urgency='medium')
    return ExecutionContext(case=case)


def test_a_valid_json_object_succeeds_no_retry(monkeypatch):
    fake_cls, calls = _make_fake_llm_client([
        ('{"status":"success","headline":"h","summary":"s"}', _usage()),
    ])
    monkeypatch.setattr(base_module, 'LLMClient', fake_cls)
    result = DummyAgent().run(_ctx())
    assert result.status == 'success'
    assert result.error is None
    assert len(calls) == 1


def test_b_valid_json_string_triggers_retry_then_succeeds(monkeypatch):
    fake_cls, calls = _make_fake_llm_client([
        ('"just a plain string, not an object"', _usage()),
        ('{"status":"success","headline":"h","summary":"s"}', _usage()),
    ])
    monkeypatch.setattr(base_module, 'LLMClient', fake_cls)
    result = DummyAgent().run(_ctx())
    assert result.status == 'success'
    assert result.error is None
    assert len(calls) == 2
    assert 'JSON object' in calls[1]  # corrective instruction was appended on retry
    assert 'JSON object' not in calls[0]


def test_c_valid_json_list_triggers_retry_then_succeeds(monkeypatch):
    fake_cls, calls = _make_fake_llm_client([
        ('[1, 2, 3]', _usage()),
        ('{"status":"success","headline":"h","summary":"s"}', _usage()),
    ])
    monkeypatch.setattr(base_module, 'LLMClient', fake_cls)
    result = DummyAgent().run(_ctx())
    assert result.status == 'success'
    assert len(calls) == 2


def test_d_second_response_valid_object_succeeds_from_real_path(monkeypatch):
    fake_cls, calls = _make_fake_llm_client([
        ('not even valid json {{{', _usage()),
        ('{"status":"success","headline":"recovered","summary":"s","confidence":0.77}', _usage()),
    ])
    monkeypatch.setattr(base_module, 'LLMClient', fake_cls)
    result = DummyAgent().run(_ctx())
    assert result.status == 'success'
    assert result.headline == 'recovered'
    assert result.confidence == 0.77
    assert len(calls) == 2
    # usage from both attempts is accounted for, not silently dropped
    assert result.metadata['usage']['total_tokens'] == 40


def test_e_second_response_still_invalid_yields_clear_failure_not_fake_success(monkeypatch):
    fake_cls, calls = _make_fake_llm_client([
        ('"still a string"', _usage()),
        ('42', _usage()),
    ])
    monkeypatch.setattr(base_module, 'LLMClient', fake_cls)
    result = DummyAgent().run(_ctx())
    assert result.status == 'failed'
    assert result.error is not None
    assert 'JSON object' in result.error
    assert 'int' in result.error  # diagnostic: reports the actual type it got back
    assert len(calls) == 2
    # must never be mistaken for a real success
    assert result.headline != 'recovered'


def test_g_findings_as_plain_strings_does_not_crash(monkeypatch):
    """Second confirmed production defect: a valid JSON *object* whose `findings`
    list contains plain strings instead of {label, detail, severity, verified}
    objects (invited by the loose `'findings': []` schema hint) crashed mk()
    with the same generic AttributeError, entirely bypassing the ask_json fix.
    This must be handled gracefully, not crash."""
    fake_cls, calls = _make_fake_llm_client([
        (
            '{"status":"success","headline":"h","summary":"s",'
            '"findings":["Missing evidence for claim A","Data incomplete for option B"]}',
            _usage(),
        ),
    ])
    monkeypatch.setattr(base_module, 'LLMClient', fake_cls)
    result = DummyAgent().run(_ctx())
    assert result.status == 'success'
    assert result.error is None
    assert len(result.findings) == 2
    assert result.findings[0].label == 'Missing evidence for claim A'
    assert len(calls) == 1  # this is a valid JSON object, no retry needed


def test_h_findings_mixed_dicts_and_strings(monkeypatch):
    fake_cls, calls = _make_fake_llm_client([
        (
            '{"status":"success","headline":"h","summary":"s",'
            '"findings":[{"label":"proper finding","detail":"d1","severity":"warn","verified":true},"a loose string finding"]}',
            _usage(),
        ),
    ])
    monkeypatch.setattr(base_module, 'LLMClient', fake_cls)
    result = DummyAgent().run(_ctx())
    assert result.status == 'success'
    assert len(result.findings) == 2
    assert result.findings[0].label == 'proper finding'
    assert result.findings[0].verified is True
    assert result.findings[1].label == 'a loose string finding'
    assert result.findings[1].verified is False


def test_f_existing_specialist_agent_behavior_unchanged_for_normal_responses(monkeypatch):
    """Sanity check: a real concrete SpecialistAgent (RiskAgent) still works
    end-to-end through the full execute()/ask_json()/mk() path when the LLM
    behaves normally — the fix must not change behavior for the common case."""
    fake_cls, calls = _make_fake_llm_client([
        (
            '{"status":"success","headline":"مخاطر محددة","summary":"تم تحديد المخاطر",'
            '"data":{"risk_level":"medium","top_risks":["a"],"mitigations":["b"]},'
            '"confidence":0.8,"warnings":[],"sources":[]}',
            _usage(),
        ),
    ])
    monkeypatch.setattr(base_module, 'LLMClient', fake_cls)
    case = CaseInput(case_id=1, title='t', description='d', urgency='medium', evidence_context=[])
    ctx = ExecutionContext(case=case)
    result = RiskAgent().run(ctx)
    assert result.status == 'success'
    assert result.data['risk_level'] == 'medium'
    assert len(calls) == 1
