from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from app.core.config import settings
from app.services.contracts import CaseInput, ExecutionContext, AgentResult
from app.services.registry import registry, SPECIALISTS
from app.services.planner import build_plan
from app.services.mock_engine import mock_result
from app.services.tools.scoring import compose_confidence, normalize_criteria, score_options, sensitivity_analysis
from app.services.fabric import hybrid_search
from app.core.ratelimit import record_usage

class Orchestrator:
    def _emit(self, callback, event_type, **payload):
        if callback:
            callback({
                'type': event_type,
                'time': datetime.now(timezone.utc).isoformat(),
                **payload,
            })

    def _run(self, name, ctx, callback=None, stage='specialist'):
        agent = registry.get(name)
        self._emit(
            callback, 'agent_start', agent=name, display_name=agent.display_name_ar,
            stage=stage, source='openai' if settings.ai_enabled and settings.ai_provider == 'openai' else 'mock'
        )

        if settings.ai_enabled and settings.ai_provider == 'openai':
            result = agent.run(ctx)
            if result.status == 'failed':
                original_error = result.error
                result = mock_result(name, ctx.case)
                result.warnings.append('openai_failed_fallback_used')
                result.metadata['fallback_reason'] = original_error
            else:
                result.metadata['analysis_source'] = 'openai'
        else:
            result = mock_result(name, ctx.case)

        event = self._event(name, result)
        event['display_name'] = agent.display_name_ar
        event['stage'] = stage
        self._emit(callback, 'agent_done', **event)
        return result

    def _event(self, name, result):
        usage = result.metadata.get('usage', {}) if result.metadata else {}
        return {
            'agent': name,
            'status': result.status,
            'duration_ms': result.duration_ms,
            'confidence': result.confidence,
            'source': result.metadata.get('analysis_source', 'python') if result.metadata else 'python',
            'error': result.error,
            'input_tokens': int(usage.get('input_tokens', 0) or 0),
            'output_tokens': int(usage.get('output_tokens', 0) or 0),
            'total_tokens': int(usage.get('total_tokens', 0) or 0),
            'estimated_cost_usd': float(result.metadata.get('estimated_cost_usd', usage.get('estimated_cost_usd', 0.0)) or 0.0) if result.metadata else 0.0,
        }

    def analyze(self, case, event_callback=None):
        try:
            case.evidence_context = hybrid_search(
                f'{case.title}\n{case.description}', case_id=case.case_id,
                tenant_id=case.tenant_id, limit=8,
            )
        except Exception:
            case.evidence_context = []
        ctx = ExecutionContext(case, response_language=(case.language or settings.response_language))
        plan = build_plan(case, SPECIALISTS)
        audit = []

        display = {n: registry.get(n).display_name_ar for n in registry.agents}
        stages = [
            {'id': 'evidence', 'label': 'فهم الأدلة', 'agents': ['evidence']},
            {'id': 'specialists', 'label': 'الخبراء المناسبون', 'agents': [x for x in plan.selected if x != 'evidence']},
            {'id': 'options', 'label': 'بناء البدائل', 'agents': ['options']},
            {'id': 'scoring', 'label': 'التقييم', 'agents': ['scoring']},
            {'id': 'critic', 'label': 'المراجعة المستقلة', 'agents': ['critic']},
            {'id': 'chief', 'label': 'التوصية التنفيذية', 'agents': ['chief_advisor']},
        ]
        self._emit(
            event_callback, 'plan',
            selected_agents=plan.selected,
            skipped_agents=plan.skipped,
            skip_reasons=plan.skip_reasons,
            stages=stages,
            display_names=display,
            execution_note='Only selected specialists run. Independent specialists run concurrently.'
        )

        evidence = self._run('evidence', ctx, event_callback, 'evidence')
        ctx.results['evidence'] = evidence
        audit.append(self._event('evidence', evidence))

        parallel = [x for x in plan.selected if x != 'evidence']
        if parallel:
            parallel_ctx = ExecutionContext(
                case=ctx.case,
                results={'evidence': evidence},
                response_language=ctx.response_language,
            )
            with ThreadPoolExecutor(max_workers=min(6, len(parallel))) as pool:
                futures = {pool.submit(self._run, n, parallel_ctx, event_callback, 'specialists'): n for n in parallel}
                for future in as_completed(futures):
                    name = futures[future]
                    result = future.result()
                    ctx.results[name] = result
                    audit.append(self._event(name, result))

        options = self._run('options', ctx, event_callback, 'options')
        ctx.results['options'] = options
        audit.append(self._event('options', options))

        self._emit(event_callback, 'agent_start', agent='scoring', display_name='محرك التقييم', stage='scoring', source='python')
        criteria=normalize_criteria(getattr(case,'scoring_criteria',None),getattr(case,'scoring_weights',None))
        scored = score_options(options.data.get('options', []), criteria=criteria)
        scoring = AgentResult(
            'scoring', 'success', 'تقييم البدائل', 'تم حساب الدرجات داخل النظام.',
            data={'options': scored,'criteria':criteria}, confidence=1,
            metadata={'analysis_source': 'python', 'estimated_cost_usd': 0.0},
        )
        ctx.results['scoring'] = scoring
        scoring_event = self._event('scoring', scoring)
        audit.append(scoring_event)
        self._emit(event_callback, 'agent_done', display_name='محرك التقييم', stage='scoring', **scoring_event)

        critic = self._run('critic', ctx, event_callback, 'critic')
        ctx.results['critic'] = critic
        audit.append(self._event('critic', critic))

        chief = self._run('chief_advisor', ctx, event_callback, 'chief')
        ctx.results['chief_advisor'] = chief
        audit.append(self._event('chief_advisor', chief))

        evidence_data = evidence.data
        chief_data = chief.data
        critic_data = critic.data
        baseline_sensitivity=sensitivity_analysis(options.data.get('options',[]),criteria)
        deterministic_confidence, confidence_breakdown = compose_confidence(
            {**evidence_data, 'sources': evidence.sources}, scored,
            clarifications=evidence_data.get('missing_information',[]),assumptions=evidence_data.get('assumptions',[]),
            conflicts=critic_data.get('challenges',[]),sensitivity=baseline_sensitivity,
        )
        any_ai = any(r.metadata.get('analysis_source') == 'openai' for r in ctx.results.values())
        total_cost = round(sum(float(x.get('estimated_cost_usd', 0) or 0) for x in audit), 6)
        total_tokens = sum(int(x.get('total_tokens', 0) or 0) for x in audit)
        total_agent_ms = sum(int(x.get('duration_ms', 0) or 0) for x in audit)
        for item in audit:
            record_usage(case.tenant_id, case.case_id, item['agent'], None,
                         item['input_tokens'], item['output_tokens'], item['estimated_cost_usd'])

        result = {
            'selected_agents': plan.selected,
            'skipped_agents': plan.skipped,
            'agent_results': {k: v.to_dict() for k, v in ctx.results.items()},
            'analysis': {
                'executive': {
                    'decision': chief_data.get('decision_label', chief.headline),
                    'recommended_option_id': chief_data.get('recommended_option_id', ''),
                    'confidence': deterministic_confidence,
                    'confidence_breakdown': confidence_breakdown,
                    'why': chief_data.get('why', []),
                    'next_actions': chief_data.get('next_actions', []),
                    'top_risks': chief_data.get('top_risks', []),
                    'decision_conditions': chief_data.get('decision_conditions', []),
                    'human_decision_required': True,
                },
                'facts': evidence_data.get('facts', []),
                'unknowns': evidence_data.get('missing_information', []),
                'readiness': evidence_data.get('readiness', 'low'),
                'evidence_sources': evidence.sources,
                'options': scored,
                'scoring_criteria':criteria,
                'calculation_metadata':{'scoring_method':'weighted-normalized-v2','confidence_method':'deterministic-v2','generated_at':datetime.now(timezone.utc).isoformat()},
                'sensitivity':baseline_sensitivity,
                'critic': critic_data,
                'run_metrics': {
                    'estimated_cost_usd': total_cost,
                    'total_tokens': total_tokens,
                    'sum_agent_duration_ms': total_agent_ms,
                    'cost_mode': 'estimate',
                    'rate_note': 'Uses configurable planning token rates; replace with contracted production rates for customer billing.',
                },
            },
            'audit_log': audit,
            'analysis_source': 'openai' if any_ai else 'mock',
        }
        self._emit(
            event_callback, 'complete',
            analysis_source=result['analysis_source'],
            estimated_cost_usd=total_cost,
            total_tokens=total_tokens,
            selected_agents=plan.selected,
        )
        return result

orchestrator = Orchestrator()
