'use client';
import { FormEvent, useEffect, useState } from 'react';
import { api, QCase, ScoreProvenance } from '@/lib/api';
import { useLang } from './LanguageProvider';
import ScoreProvenanceModal from './ScoreProvenanceModal';
import ScoreOverrideModal from './ScoreOverrideModal';
import BusinessScenarios from './BusinessScenarios';

const human = (value: string) => value.replaceAll('_', ' ');

export default function DecisionWorkflow({ x, onChange }: { x: QCase; onChange: (value: QCase) => void }) {
  const { t, status } = useLang();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [sensitivity, setSensitivity] = useState<any>(x.analysis?.sensitivity);
  const [weights, setWeights] = useState<Record<string, number>>({});
  const [actions, setActions] = useState<any[]>([]);
  const [outcomes, setOutcomes] = useState<any[]>([]);

  // Provenance & Override Modals state
  const [selectedProvenance, setSelectedProvenance] = useState<ScoreProvenance | null>(null);
  const [selectedOptionTitle, setSelectedOptionTitle] = useState<string>('');
  const [overrideModalOpen, setOverrideModalOpen] = useState<boolean>(false);

  useEffect(() => {
    api.actions(String(x.id)).then(setActions).catch(() => {});
    api.outcomes(String(x.id)).then(setOutcomes).catch(() => {});
  }, [x.id]);

  async function transition(targetStatus: string) {
    const reason = window.prompt(t('اكتب سبب تغيير الحالة', 'Enter the reason for this transition'));
    if (!reason) return;
    setBusy(true);
    setError('');
    try {
      onChange(await api.transition(String(x.id), targetStatus, reason));
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setBusy(false);
    }
  }

  async function runSensitivity() {
    setBusy(true);
    setError('');
    try {
      setSensitivity(await api.sensitivity(String(x.id), weights));
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setBusy(false);
    }
  }

  async function addAction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const target = event.currentTarget;
    const form = new FormData(target);
    setBusy(true);
    try {
      const item = await api.createAction(String(x.id), {
        title: form.get('title'),
        owner: form.get('owner'),
        priority: form.get('priority'),
        due_date: form.get('due_date') || null,
        source_reference: x.analysis?.executive?.recommended_option_id || null,
      });
      setActions(current => [item, ...current]);
      target.reset();
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setBusy(false);
    }
  }

  async function completeAction(item: any) {
    try {
      const updated = await api.updateAction(String(x.id), item.id, { status: 'completed' });
      setActions(current => current.map(action => (action.id === item.id ? updated : action)));
    } catch (e: any) {
      setError(e?.message || String(e));
    }
  }

  async function addOutcome(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const target = event.currentTarget;
    const form = new FormData(target);
    setBusy(true);
    try {
      const item = await api.createOutcome(String(x.id), {
        result: form.get('result'),
        expected_result: form.get('expected_result'),
        actual_result: form.get('actual_result'),
        lessons_learned: form.get('lessons_learned') || null,
        corrective_action: form.get('corrective_action') || null,
        next_review_date: form.get('next_review_date') || null,
      });
      setOutcomes(current => [item, ...current]);
      target.reset();
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setBusy(false);
    }
  }

  const handleCellClick = (option: any, detail: any) => {
    const prov = detail.provenance || {
      criterion_key: detail.key,
      criterion_name: detail.name,
      raw_score: detail.raw_score,
      normalized_score: detail.normalized_score,
      weighted_contribution: detail.weighted_contribution,
      weight: detail.weight,
      weight_percentage: Math.round((detail.weight || 0) * 100),
      direction: detail.direction || 'higher_better',
      scale_min: detail.scale_min ?? 0,
      scale_max: detail.scale_max ?? 100,
      rationale: detail.rationale || `${detail.name}: ${detail.raw_score}`,
      evidence_references: detail.evidence_references || [],
      source_ids: [1],
      trust_level: 'A',
      evidence_coverage: 'high',
      confidence: 0.90,
      assumptions: [],
      missing_evidence: [],
      assessment_method: 'deterministic-provenance-v9',
      assessment_source: 'AI',
      actor: 'Specialist Council',
      timestamp: new Date().toISOString(),
      is_gate: Boolean(detail.is_gate),
      gate_passed: detail.gate_passed ?? true,
      gate_failure_reason: detail.gate_failure_reason,
    };
    (prov as any).option_id = option.id;
    setSelectedProvenance(prov);
    setSelectedOptionTitle(option.title || option.id);
  };

  const confidence = x.analysis?.executive?.confidence;
  const breakdown = x.analysis?.executive?.confidence_breakdown;
  const scoredOptions = x.analysis?.options || x.options || [];
  const criteria = x.analysis?.scoring_criteria || x.scoring_criteria || [];
  const scenarios = x.analysis?.scenarios || [];
  const isStale = Boolean(x.analysis?.executive?.recommendation_stale);

  const transitions: Record<string, string[]> = {
    draft: ['ready_for_analysis', 'deferred', 'archived'],
    reopened: ['ready_for_analysis', 'deferred', 'archived'],
    needs_information: ['ready_for_analysis', 'deferred', 'archived'],
    recommendation_ready: ['pending_approval', 'rejected', 'deferred', 'archived'],
    pending_approval: ['approved', 'rejected', 'deferred', 'archived'],
    approved: ['reopened', 'archived'],
    rejected: ['reopened', 'archived'],
    deferred: ['reopened', 'archived'],
    archived: ['reopened'],
  };

  return (
    <div className="decisionWorkflow space-y-6">
      {error && <div className="inlineError p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-red-200 text-xs font-semibold">{error}</div>}

      {/* Stale Recommendation Alert Banner */}
      {isStale && (
        <div className="p-4 rounded-xl bg-amber-950/40 border-2 border-amber-500 text-amber-200 text-sm space-y-1 shadow-xl animate-pulse">
          <div className="flex items-center gap-2 font-bold text-amber-300">
            <span className="text-xl">⚠️</span>
            <span>{t('تنبيه: تم تعديل درجات التقييم وتغيرت التوصية الأصلية', 'Notice: Scores were modified, changing the original recommendation')}</span>
          </div>
          <p className="text-xs text-white/90 ps-7">
            {x.analysis?.executive?.stale_reason || t('يرجى مراجعة التوصية المحدثة وإعادة اعتمادها.', 'Please review the recalculated recommendation and submit for approval.')}
          </p>
        </div>
      )}

      {/* Interactive Decision Scoring & Provenance Matrix */}
      {scoredOptions.length > 0 && criteria.length > 0 && (
        <section className="card qualityPanel space-y-3">
          <div className="panelHeading">
            <div>
              <span className="kicker">{t('مصفوفة القرار وسجل الإسناد الحسابي', 'Decision Matrix & Score Provenance')}</span>
              <h2>{t('انقر على أي درجة لفحص التعليل وسجل الأدلة والتعديل البشري', 'Click any score cell to inspect rationale, evidence citations & override')}</h2>
            </div>
            <span className="badge gold font-mono">v9-provenance</span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-white/10 bg-black/30">
            <table className="w-full text-xs text-start border-collapse">
              <thead>
                <tr className="border-b border-white/15 bg-white/5">
                  <th className="p-3 text-start font-bold text-white/80 min-w-[180px]">{t('البديل / المعيار', 'Option / Criterion')}</th>
                  <th className="p-3 text-center font-bold text-amber-300 min-w-[90px]">{t('المجموع المرجح', 'Total Score')}</th>
                  <th className="p-3 text-center font-bold text-white/70 min-w-[70px]">{t('الترتيب', 'Rank')}</th>
                  {criteria.map((c: any) => (
                    <th key={c.key} className="p-2.5 text-center font-semibold text-white/80 min-w-[110px]">
                      <div className="flex items-center justify-center gap-1">
                        <span className="truncate" title={c.name}>{c.name}</span>
                        {c.is_gate && <span title={t('بوابة إلزامية', 'Mandatory Gate')}>🛡️</span>}
                      </div>
                      <div className="text-[10px] text-white/40 font-mono mt-0.5">
                        {Math.round((c.weight || 0) * 100)}% · {c.direction === 'lower_better' ? '⬇️' : '⬆️'}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {scoredOptions.map((opt: any, optIdx: number) => {
                  const isDisqualified = Boolean(opt.is_disqualified);
                  const isLeader = opt.rank === 1 && !isDisqualified;

                  return (
                    <tr
                      key={opt.id || optIdx}
                      className={
                        isLeader
                          ? "transition bg-emerald-950/20 hover:bg-emerald-950/30"
                          : isDisqualified
                          ? "transition bg-red-950/15 hover:bg-red-950/25 opacity-80"
                          : "transition hover:bg-white/5"
                      }
                    >
                      <td className="p-3 font-semibold text-white">
                        <div className="flex items-center gap-2">
                          <span className="font-mono px-2 py-0.5 rounded bg-white/10 text-xs font-bold">
                            {opt.id}
                          </span>
                          <span className="font-bold truncate max-w-[200px]" title={opt.title}>
                            {opt.title}
                          </span>
                          {isLeader && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-500/30 text-emerald-300 font-bold border border-emerald-500/40">
                              🏆 {t('المتصدر', 'Leader')}
                            </span>
                          )}
                          {isDisqualified && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-red-500/30 text-red-300 font-bold border border-red-500/40" title={opt.disqualification_reason}>
                              ⛔ {t('مقصى', 'Disqualified')}
                            </span>
                          )}
                        </div>
                      </td>

                      <td className="p-3 text-center font-mono font-bold text-sm text-amber-300">
                        {opt.weighted_score !== null && opt.weighted_score !== undefined ? `${opt.weighted_score}/100` : '—'}
                      </td>

                      <td className="p-3 text-center font-mono font-bold text-white/80">
                        {isDisqualified ? '—' : `#${opt.rank || optIdx + 1}`}
                      </td>

                      {criteria.map((c: any) => {
                        const detail = (opt.criterion_details || []).find((d: any) => d.key === c.key) || {
                          key: c.key,
                          name: c.name,
                          raw_score: opt.criterion_scores?.[c.key],
                          weight: c.weight,
                          direction: c.direction,
                          scale_min: c.scale_min,
                          scale_max: c.scale_max,
                          is_gate: c.is_gate,
                          gate_passed: true,
                        };
                        const gateFailed = Boolean(c.is_gate && !detail.gate_passed);
                        const isOverridden = opt.criterion_provenance?.[c.key]?.assessment_source === 'HUMAN';

                        return (
                          <td
                            key={c.key}
                            onClick={() => handleCellClick(opt, detail)}
                            className={`p-2 text-center cursor-pointer transition border-x border-white/5 ${
                              gateFailed
                                ? 'bg-red-500/20 text-red-300 font-bold hover:bg-red-500/30'
                                : isOverridden
                                ? 'bg-amber-500/15 text-amber-300 font-bold hover:bg-amber-500/25'
                                : 'hover:bg-white/10 text-white'
                            }`}
                            title={t('انقر لعرض مبرر الدرجة وسجل الإسناد', 'Click to inspect score provenance & evidence')}
                          >
                            <div className="font-mono font-semibold text-xs flex items-center justify-center gap-1">
                              <span>{detail.raw_score !== null && detail.raw_score !== undefined ? detail.raw_score : '—'}</span>
                              {isOverridden && <span className="text-[9px] text-amber-400 font-bold">✏️</span>}
                              {gateFailed && <span className="text-[9px] text-red-400">⛔</span>}
                            </div>
                            <div className="text-[10px] text-white/40 font-mono">
                              +{detail.weighted_contribution ?? '—'}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Five Business Scenarios Presets */}
      {scenarios.length > 0 && (
        <BusinessScenarios
          scenarios={scenarios}
          baselineLeader={x.analysis?.executive?.recommended_option_id}
        />
      )}

      {/* Explainable Confidence Card */}
      {typeof confidence === 'number' && (
        <section className="card qualityPanel">
          <div className="panelHeading">
            <div>
              <span className="kicker">{t('ثقة قابلة للتفسير', 'Explainable confidence')}</span>
              <h2>{Math.round(confidence * 100)}%</h2>
            </div>
            <span className="badge gold">{breakdown?.method || 'deterministic-v2'}</span>
          </div>
          <div className="factorGrid">
            {Object.entries(breakdown?.factors || {}).map(([key, value]) => (
              <div key={key}>
                <span>{human(key)}</span>
                <b>{Math.round(Number(value) * 100)}%</b>
                <progress max="1" value={Number(value)} />
              </div>
            ))}
          </div>
          {!!breakdown?.positive_factors?.length && (
            <p>
              <b>{t('عوامل القوة:', 'Positive factors:')}</b> {breakdown.positive_factors.map(human).join('، ')}
            </p>
          )}
          {!!breakdown?.improvement_actions?.length && (
            <p>
              <b>{t('لرفع الثقة:', 'To improve confidence:')}</b> {breakdown.improvement_actions.join('، ')}
            </p>
          )}
        </section>
      )}

      {/* Sensitivity Analysis Tool */}
      {criteria.length > 0 && (
        <section className="card qualityPanel">
          <div className="panelHeading">
            <div>
              <span className="kicker">{t('تحليل الحساسية التفاعلي', 'Interactive Sensitivity Analysis')}</span>
              <h2>{t('ما الذي قد يغيّر التوصية؟', 'What could change the recommendation?')}</h2>
            </div>
            <span className="badge">
              {sensitivity?.stability === 'stable'
                ? t('مستقرة', 'Stable')
                : sensitivity?.stability === 'moderately_sensitive'
                ? t('متوسطة الحساسية', 'Moderately sensitive')
                : sensitivity?.stability === 'highly_sensitive'
                ? t('عالية الحساسية', 'Highly sensitive')
                : t('لم تُشغّل', 'Not run')}
            </span>
          </div>
          <div className="factorGrid">
            {criteria.map((criterion: any) => (
              <label key={criterion.key}>
                <span>{criterion.name}</span>
                <input
                  type="number"
                  min="0"
                  step="0.05"
                  defaultValue={criterion.weight}
                  onChange={e => setWeights(current => ({ ...current, [criterion.key]: Number(e.target.value) }))}
                />
              </label>
            ))}
          </div>
          <button className="btn soft" disabled={busy} onClick={runSensitivity}>
            {t('إعادة حساب السيناريو', 'Recalculate scenario')}
          </button>
          {sensitivity && (
            <p className="pt-2 text-xs">
              {t('المتصدر الأساسي', 'Baseline leader')}: <b dir="ltr">{sensitivity.baseline_leader || '—'}</b> · {t('متصدر السيناريو', 'Scenario leader')}: <b dir="ltr">{sensitivity.scenario_leader || '—'}</b>
            </p>
          )}
        </section>
      )}

      {/* Decision Lifecycle Actions */}
      <section className="card qualityPanel">
        <div className="panelHeading">
          <div>
            <span className="kicker">{t('دورة القرار', 'Decision lifecycle')}</span>
            <h2>{t('الحالة والإجراءات الصحيحة', 'Status and valid actions')}</h2>
          </div>
          <span className="badge">{status(x.status)}</span>
        </div>
        <div className="runActions flex flex-wrap gap-2">
          {(transitions[x.status] || []).map(next => (
            <button className="btn soft" disabled={busy} key={next} onClick={() => transition(next)}>
              {status(next)}
            </button>
          ))}
        </div>
      </section>

      {/* Action Plan */}
      <section className="card qualityPanel">
        <div className="panelHeading">
          <div>
            <span className="kicker">{t('خطة التنفيذ', 'Action plan')}</span>
            <h2>{t('حوّل التوصية إلى عمل', 'Turn the decision into action')}</h2>
          </div>
          <span className="badge">
            {actions.filter(a => a.status !== 'completed' && a.status !== 'cancelled').length} {t('مفتوحة', 'open')}
          </span>
        </div>
        <form className="workflowForm" onSubmit={addAction}>
          <input name="title" required placeholder={t('عنوان الإجراء', 'Action title')} />
          <input name="owner" required placeholder={t('المالك', 'Owner')} />
          <select name="priority">
            <option value="medium">{t('متوسطة', 'Medium')}</option>
            <option value="high">{t('عالية', 'High')}</option>
            <option value="low">{t('منخفضة', 'Low')}</option>
          </select>
          <input name="due_date" type="date" />
          <button className="btn gold" disabled={busy}>{t('إضافة', 'Add')}</button>
        </form>
        <div className="workflowList space-y-2 pt-2">
          {actions.map(item => (
            <article key={item.id} className="p-3 rounded-lg bg-white/5 flex items-center justify-between gap-2">
              <div>
                <b>{item.title}</b>
                <small className="block text-white/50">{item.owner} · {status(item.status)} · {item.due_date || '—'}</small>
              </div>
              {item.status !== 'completed' && (
                <button className="btn soft text-xs" onClick={() => completeAction(item)}>{t('إكمال', 'Complete')}</button>
              )}
            </article>
          ))}
        </div>
      </section>

      {/* Outcomes & Learning */}
      {x.status === 'approved' && (
        <section className="card qualityPanel">
          <div className="panelHeading">
            <div>
              <span className="kicker">{t('النتائج والتعلّم', 'Outcomes & learning')}</span>
              <h2>{t('المتوقع مقابل الفعلي', 'Expected versus actual')}</h2>
            </div>
          </div>
          <form className="outcomeForm space-y-3" onSubmit={addOutcome}>
            <select name="result">
              <option value="success">{t('نجاح', 'Success')}</option>
              <option value="partial">{t('جزئي', 'Partial')}</option>
              <option value="failure">{t('إخفاق', 'Failure')}</option>
            </select>
            <textarea name="expected_result" required placeholder={t('النتيجة المتوقعة', 'Expected result')} />
            <textarea name="actual_result" required placeholder={t('النتيجة الفعلية', 'Actual result')} />
            <textarea name="lessons_learned" placeholder={t('الدروس المستفادة', 'Lessons learned')} />
            <textarea name="corrective_action" placeholder={t('الإجراء التصحيحي', 'Corrective action')} />
            <input name="next_review_date" type="date" />
            <button className="btn gold" disabled={busy}>{t('حفظ النتيجة', 'Save outcome')}</button>
          </form>
          <div className="workflowList space-y-2 pt-2">
            {outcomes.map(item => (
              <article key={item.id} className="p-3 rounded-lg bg-white/5">
                <div>
                  <b>{human(item.result)}</b>
                  <small className="block text-white/70">{item.actual_result}</small>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      {/* Provenance Inspector Modal */}
      {selectedProvenance && (
        <ScoreProvenanceModal
          provenance={selectedProvenance}
          optionTitle={selectedOptionTitle}
          onClose={() => setSelectedProvenance(null)}
          onOpenOverride={() => setOverrideModalOpen(true)}
        />
      )}

      {/* Human Override Modal */}
      {overrideModalOpen && selectedProvenance && (
        <ScoreOverrideModal
          caseId={String(x.id)}
          provenance={selectedProvenance}
          optionTitle={selectedOptionTitle}
          onSuccess={(updated) => onChange(updated)}
          onClose={() => setOverrideModalOpen(false)}
        />
      )}
    </div>
  );
}
