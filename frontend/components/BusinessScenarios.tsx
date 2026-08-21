'use client';
import { useState } from 'react';
import { ScenarioPreset } from '@/lib/api';
import { useLang } from './LanguageProvider';

interface BusinessScenariosProps {
  scenarios: ScenarioPreset[];
  baselineLeader?: string;
}

export default function BusinessScenarios({ scenarios, baselineLeader }: BusinessScenariosProps) {
  const { t, lang } = useLang();
  const [selectedPresetId, setSelectedPresetId] = useState<string>(
    scenarios?.[0]?.preset_id || scenarios?.[0]?.id || 'balanced'
  );

  if (!scenarios || scenarios.length === 0) return null;

  const current = scenarios.find(s => (s.preset_id || s.id) === selectedPresetId) || scenarios[0];

  return (
    <section className="card qualityPanel space-y-4">
      <div className="panelHeading">
        <div>
          <span className="kicker">{t('سيناريوهات الأعمال الخمسة', 'Five Business Scenarios')}</span>
          <h2>{t('تحليل متانة القرار عبر الأولويات الاستراتيجية المختلفة', 'Decision Robustness Across Strategic Priorities')}</h2>
        </div>
        <span className={current.stability === 'stable' ? 'badge gold' : current.stability === 'moderately_sensitive' ? 'badge' : 'badge danger'}>
          {current.stability === 'stable' ? t('متانة عالية (مستقر)', 'High Stability') : current.stability === 'moderately_sensitive' ? t('متوسط الحساسية', 'Moderate') : t('عالي الحساسية', 'Sensitive')}
        </span>
      </div>

      {/* Preset Selector Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
        {scenarios.map(s => {
          const pid = s.preset_id || s.id || '';
          const active = pid === selectedPresetId;
          const title = lang === 'ar' ? s.title_ar : s.title_en;

          return (
            <button
              key={pid}
              type="button"
              onClick={() => setSelectedPresetId(pid)}
              className={
                active
                  ? "p-3 rounded-xl border text-start transition flex flex-col justify-between gap-1.5 bg-amber-500/20 border-amber-500/50 text-white shadow-lg"
                  : "p-3 rounded-xl border text-start transition flex flex-col justify-between gap-1.5 bg-white/5 border-white/10 text-white/70 hover:bg-white/10 hover:text-white"
              }
            >
              <div className="flex items-center justify-between w-full">
                <span className="font-bold text-xs truncate">{title}</span>
                {s.leader_changed && (
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-500/30 text-amber-300 font-bold" title={t('تغير المتصدر في هذا السيناريو', 'Leader changed in this scenario')}>
                    ⚡
                  </span>
                )}
              </div>
              <div className="text-[11px] font-mono text-white/50">
                {t('المتصدر:', 'Leader:')} <b className="text-white">{s.scenario_leader || '—'}</b>
              </div>
            </button>
          );
        })}
      </div>

      {/* Active Scenario Card */}
      {current && (
        <div className="p-4 rounded-xl bg-black/40 border border-white/10 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 pb-2.5 text-xs">
            <div>
              <h3 className="font-bold text-white text-sm">
                {lang === 'ar' ? current.title_ar : current.title_en}
              </h3>
              <p className="text-white/60 text-xs mt-0.5">
                {lang === 'ar' ? current.description_ar : current.description_en}
              </p>
            </div>
            <div className="flex items-center gap-3 font-mono">
              <div>
                <span className="text-white/50">{t('المتصدر الأساسي:', 'Baseline:')}</span>{' '}
                <b className="text-white/80">{current.baseline_leader || baselineLeader || '—'}</b>
              </div>
              <div>
                <span className="text-white/50">{t('متصدر السيناريو:', 'Scenario Leader:')}</span>{' '}
                <b className="text-emerald-400 text-sm font-bold">{current.scenario_leader || '—'}</b>
              </div>
              <div>
                <span className="text-white/50">{t('الفارق:', 'Margin:')}</span>{' '}
                <b className="text-amber-300">+{current.margin ?? 0} {t('نقطة', 'pts')}</b>
              </div>
            </div>
          </div>

          {/* Explanation Text */}
          <div className="p-3 rounded-lg bg-white/5 border border-white/10 text-xs text-white/90 leading-relaxed flex items-start gap-2">
            <span>💡</span>
            <span>{lang === 'ar' ? current.explanation_ar : current.explanation_en}</span>
          </div>

          {/* Weights Distribution Pill */}
          {current.weights && Object.keys(current.weights).length > 0 && (
            <div className="pt-1">
              <div className="text-[11px] text-white/50 mb-1.5">{t('توزيع الأوزان في هذا السيناريو:', 'Scenario Weight Distribution:')}</div>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(current.weights).map(([k, w]) => (
                  <span key={k} className="text-[11px] px-2 py-0.5 rounded bg-white/10 text-white/80 font-mono">
                    {k}: <b>{Math.round(Number(w) * 100)}%</b>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
