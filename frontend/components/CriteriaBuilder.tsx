'use client';
import { useState } from 'react';
import { ScoringCriterion } from '@/lib/api';
import { useLang } from './LanguageProvider';

export interface CriteriaBuilderProps {
  criteria: ScoringCriterion[];
  onChange: (criteria: ScoringCriterion[]) => void;
  disabled?: boolean;
}

export const DEFAULT_CRITERIA_PRESET: ScoringCriterion[] = [
  { key: 'compliance', name: 'الامتثال والضوابط', description: 'التوافق مع المتطلبات النظامية والتشريعية', weight: 0.25, scale_min: 0, scale_max: 100, direction: 'higher_better', is_gate: true, gate_min: 80, evidence_requirement: 'شهادات الامتثال أو تقارير التدقيق' },
  { key: 'risk', name: 'إدارة المخاطر والأمان', description: 'القدرة على خفض المخاطر السيبرانية والتشغيلية', weight: 0.20, scale_min: 0, scale_max: 100, direction: 'higher_better', is_gate: false, evidence_requirement: 'سجل تقييم المخاطر وخطة المعالجة' },
  { key: 'financial', name: 'الكفاءة والتكلفة المالية', description: 'التكلفة الإجمالية للملكية والقيمة الاستثمارية', weight: 0.20, scale_min: 0, scale_max: 100, direction: 'higher_better', is_gate: false, evidence_requirement: 'نموذج التكلفة الإجمالية TCO والعرض المالي' },
  { key: 'time', name: 'سرعة الإنجاز والجاهزية', description: 'الجدول الزمني للتسليم وسرعة تحقيق القيمة', weight: 0.15, scale_min: 0, scale_max: 100, direction: 'higher_better', is_gate: false, evidence_requirement: 'خطة وجدول التنفيذ الزمني' },
  { key: 'strategy', name: 'المواءمة الاستراتيجية', description: 'مساهمة القرار في تحقيق الأهداف المؤسسية', weight: 0.10, scale_min: 0, scale_max: 100, direction: 'higher_better', is_gate: false, evidence_requirement: 'وثيقة التوافق مع الخطة الاستراتيجية' },
  { key: 'stakeholder', name: 'ملاءمة أصحاب المصلحة', description: 'سهولة التبني ومستوى الرضا', weight: 0.10, scale_min: 0, scale_max: 100, direction: 'higher_better', is_gate: false, evidence_requirement: 'استطلاع أو ملاحظات أصحاب المصلحة' },
];

export default function CriteriaBuilder({ criteria, onChange, disabled }: CriteriaBuilderProps) {
  const { t } = useLang();
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const totalRawWeight = (criteria || []).reduce((sum, c) => sum + (Number(c.weight) || 0), 0);

  const handleUpdate = (index: number, updates: Partial<ScoringCriterion>) => {
    const updated = [...(criteria || [])];
    updated[index] = { ...updated[index], ...updates };
    onChange(updated);
  };

  const handleAdd = () => {
    const list = criteria || [];
    const key = 'criterion_' + (list.length + 1);
    const newCrit: ScoringCriterion = {
      key,
      name: t('معيار جديد', 'New Criterion') + ' ' + (list.length + 1),
      description: '',
      weight: 0.10,
      scale_min: 0,
      scale_max: 100,
      direction: 'higher_better',
      is_gate: false,
      gate_min: null,
      gate_max: null,
      evidence_requirement: '',
    };
    onChange([...list, newCrit]);
    setEditingIndex(list.length);
  };

  const handleRemove = (index: number) => {
    if ((criteria || []).length <= 1) return;
    const updated = criteria.filter((_, i) => i !== index);
    onChange(updated);
    if (editingIndex === index) setEditingIndex(null);
  };

  const handleNormalize = () => {
    if (totalRawWeight <= 0) return;
    const normalized = (criteria || []).map(c => ({
      ...c,
      weight: Math.round(((Number(c.weight) || 0) / totalRawWeight) * 100) / 100
    }));
    onChange(normalized);
  };

  const handleResetDefault = () => {
    onChange(DEFAULT_CRITERIA_PRESET);
  };

  return (
    <div className="criteriaBuilder space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-3">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <span>⚖️</span>
            {t('بناء معايير التقييم والأوزان والبوابات', 'Criteria Builder, Weights & Mandatory Gates')}
          </h3>
          <p className="text-xs text-white/60">
            {t('حدد المعايير المرجحة والبوابات الإلزامية التي تقصي البدائل غير المستوفية للشروط', 'Configure weighted criteria and mandatory qualification gates that disqualify non-compliant options.')}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={
            Math.abs(totalRawWeight - 1.0) < 0.01 || Math.abs(totalRawWeight - 100) < 0.5
              ? "text-xs px-2.5 py-1 rounded-full font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
              : "text-xs px-2.5 py-1 rounded-full font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30"
          }>
            {t('مجموع الأوزان:', 'Total Weight:')} {Math.round(totalRawWeight * 100)}%
          </span>
          {!disabled && (
            <>
              <button type="button" onClick={handleNormalize} className="text-xs px-2.5 py-1 bg-white/10 hover:bg-white/20 text-white rounded transition">
                {t('موازنة الأوزان (100%)', 'Normalize to 100%')}
              </button>
              <button type="button" onClick={handleResetDefault} className="text-xs px-2 py-1 text-white/60 hover:text-white transition">
                {t('استعادة الافتراضي', 'Reset Defaults')}
              </button>
            </>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {(criteria || []).map((c, idx) => {
          const isGate = Boolean(c.is_gate);
          const weightPercent = totalRawWeight > 0 ? Math.round(((Number(c.weight) || 0) / totalRawWeight) * 100) : 0;

          return (
            <div
              key={c.key || idx}
              className={
                isGate
                  ? "p-3.5 rounded-xl border transition bg-amber-950/20 border-amber-500/40 hover:border-white/25"
                  : "p-3.5 rounded-xl border transition bg-white/5 border-white/10 hover:border-white/25"
              }
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2.5 flex-1 min-w-[220px]">
                  <span className="text-xs font-mono text-white/40">#{idx + 1}</span>
                  <input
                    type="text"
                    disabled={disabled}
                    value={c.name}
                    onChange={e => handleUpdate(idx, { name: e.target.value })}
                    placeholder={t('اسم المعيار', 'Criterion Name')}
                    className="bg-transparent font-semibold text-sm text-white focus:outline-none focus:bg-white/10 px-2 py-1 rounded w-full max-w-sm"
                  />
                  {isGate && (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 whitespace-nowrap">
                      <span>🛡️</span>
                      {t('بوابة إلزامية', 'Mandatory Gate')}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <label className="text-xs text-white/60">{t('الوزن:', 'Weight:')}</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.05"
                      disabled={disabled}
                      value={c.weight}
                      onChange={e => handleUpdate(idx, { weight: parseFloat(e.target.value) || 0 })}
                      className="w-16 bg-black/40 border border-white/20 text-white rounded px-2 py-1 text-xs text-center font-mono"
                    />
                    <span className="text-xs text-white/50 font-mono">({weightPercent}%)</span>
                  </div>

                  <select
                    disabled={disabled}
                    value={c.direction || 'higher_better'}
                    onChange={e => handleUpdate(idx, { direction: e.target.value as any })}
                    className="bg-black/40 border border-white/20 text-white rounded px-2 py-1 text-xs"
                  >
                    <option value="higher_better">{t('الأعلى أفضل ⬆️', 'Higher is better ⬆️')}</option>
                    <option value="lower_better">{t('الأقل أفضل ⬇️ (تكلفة/زمن)', 'Lower is better ⬇️ (Cost/Time)')}</option>
                  </select>

                  <button
                    type="button"
                    disabled={disabled}
                    onClick={() => setEditingIndex(editingIndex === idx ? null : idx)}
                    className="text-xs px-2.5 py-1 bg-white/10 hover:bg-white/20 text-white rounded"
                  >
                    {editingIndex === idx ? t('إخفاء التفاصيل', 'Hide') : t('إعدادات وبوابة', 'Gate & Settings')}
                  </button>

                  {!disabled && (criteria || []).length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemove(idx)}
                      className="text-xs text-red-400 hover:text-red-300 px-1.5 py-1"
                      title={t('حذف المعيار', 'Delete criterion')}
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>

              {editingIndex === idx && (
                <div className="mt-3 pt-3 border-t border-white/10 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="block text-white/70 mb-1">{t('وصف المعيار', 'Description')}</label>
                    <input
                      type="text"
                      disabled={disabled}
                      value={c.description || ''}
                      onChange={e => handleUpdate(idx, { description: e.target.value })}
                      placeholder={t('شرح موجز لما يقيسه هذا المعيار', 'Brief explanation of what this criterion measures')}
                      className="w-full bg-black/40 border border-white/20 text-white rounded px-2.5 py-1.5"
                    />
                  </div>

                  <div>
                    <label className="block text-white/70 mb-1">{t('متطلب الدليل والتحقق', 'Evidence Requirement')}</label>
                    <input
                      type="text"
                      disabled={disabled}
                      value={c.evidence_requirement || ''}
                      onChange={e => handleUpdate(idx, { evidence_requirement: e.target.value })}
                      placeholder={t('اسم المستند أو الشهادة المطلوبة للتحقق', 'Document or certification required for verification')}
                      className="w-full bg-black/40 border border-white/20 text-white rounded px-2.5 py-1.5"
                    />
                  </div>

                  <div className="md:col-span-2 p-2.5 bg-black/30 rounded-lg border border-white/10 flex flex-wrap items-center justify-between gap-3">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        disabled={disabled}
                        checked={isGate}
                        onChange={e => handleUpdate(idx, { is_gate: e.target.checked })}
                        className="rounded border-white/30 text-amber-500 focus:ring-0 w-4 h-4"
                      />
                      <div>
                        <span className="font-bold text-white text-xs block">
                          {t('تفعيل كبوابة إلزامية (Mandatory Gate)', 'Enforce as Mandatory Gate')}
                        </span>
                        <span className="text-[11px] text-white/50">
                          {t('إقصاء أي بديل يفشل في تجاوز العتبة المحددة تلقائياً', 'Automatically disqualify any option that fails this threshold.')}
                        </span>
                      </div>
                    </label>

                    {isGate && (
                      <div className="flex items-center gap-2">
                        <label className="text-white/80">
                          {c.direction === 'lower_better' ? t('الحد الأقصى المسموح (سقف):', 'Maximum allowed cap:') : t('الحد الأدنى للنجاح (عتبة):', 'Minimum passing threshold:')}
                        </label>
                        <input
                          type="number"
                          disabled={disabled}
                          value={c.direction === 'lower_better' ? (c.gate_max ?? 50) : (c.gate_min ?? 75)}
                          onChange={e => {
                            const val = parseFloat(e.target.value) || 0;
                            if (c.direction === 'lower_better') {
                              handleUpdate(idx, { gate_max: val });
                            } else {
                              handleUpdate(idx, { gate_min: val });
                            }
                          }}
                          className="w-20 bg-black/60 border border-amber-500/50 text-amber-300 font-mono font-bold rounded px-2 py-1 text-center"
                        />
                        <span className="text-white/40">/ 100</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {!disabled && (
        <button
          type="button"
          onClick={handleAdd}
          className="w-full py-2 border-2 border-dashed border-white/20 hover:border-white/40 rounded-xl text-xs font-semibold text-white/80 hover:text-white transition flex items-center justify-center gap-2"
        >
          <span>➕</span>
          {t('إضافة معيار تقييم جديد', 'Add New Scoring Criterion')}
        </button>
      )}
    </div>
  );
}
