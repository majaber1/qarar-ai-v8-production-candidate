'use client';
import { useState } from 'react';
import { DecisionOption, ScoringCriterion } from '@/lib/api';
import { useLang } from './LanguageProvider';

interface OptionsEditorProps {
  options: DecisionOption[];
  criteria?: ScoringCriterion[];
  onChange: (options: DecisionOption[]) => void;
  disabled?: boolean;
}

export default function OptionsEditor({ options, criteria, onChange, disabled }: OptionsEditorProps) {
  const { t } = useLang();
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const handleUpdate = (index: number, updates: Partial<DecisionOption>) => {
    const updated = [...options];
    updated[index] = { ...updated[index], ...updates };
    onChange(updated);
  };

  const handleAdd = () => {
    const id = 'opt_' + (options.length + 1);
    const newOpt: DecisionOption = {
      id,
      title: t('بديل جديد', 'New Option') + ' ' + String.fromCharCode(65 + options.length),
      description: '',
      benefits: [],
      risks: [],
      conditions: [],
      criterion_scores: {},
    };
    onChange([...options, newOpt]);
    setEditingIndex(options.length);
  };

  const handleRemove = (index: number) => {
    if (options.length <= 1) return;
    const updated = options.filter((_, i) => i !== index);
    onChange(updated);
    if (editingIndex === index) setEditingIndex(null);
  };

  return (
    <div className="optionsEditor space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-3">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <span>🎯</span>
            {t('البدائل والخيارات المطروحة للمفاضلة', 'Decision Options for Evaluation')}
          </h3>
          <p className="text-xs text-white/60">
            {t('أدخل البدائل المحددة لديك أو اتركها لـ Qarar لتوليد مسارات مقترحة للمفاضلة', 'Define your explicit options or let Qarar generate balanced candidate paths.')}
          </p>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full bg-white/10 text-white font-mono font-bold">
          {options.length} {t('بدائل', 'options')}
        </span>
      </div>

      <div className="space-y-3">
        {options.map((opt, idx) => (
          <div
            key={opt.id || idx}
            className="p-3.5 rounded-xl border border-white/10 bg-white/5 hover:border-white/25 transition space-y-2"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2.5 flex-1 min-w-[220px]">
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {opt.id || `#${idx + 1}`}
                </span>
                <input
                  type="text"
                  disabled={disabled}
                  value={opt.title}
                  onChange={e => handleUpdate(idx, { title: e.target.value })}
                  placeholder={t('عنوان البديل (مثال: منصة أزور السحابية)', 'Option Title (e.g. Microsoft Azure)')}
                  className="bg-transparent font-semibold text-sm text-white focus:outline-none focus:bg-white/10 px-2 py-1 rounded w-full max-w-sm"
                />
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={disabled}
                  onClick={() => setEditingIndex(editingIndex === idx ? null : idx)}
                  className="text-xs px-2.5 py-1 bg-white/10 hover:bg-white/20 text-white rounded"
                >
                  {editingIndex === idx ? t('إخفاء', 'Hide') : t('تفاصيل ودرجات', 'Details & Scores')}
                </button>

                {!disabled && options.length > 1 && (
                  <button
                    type="button"
                    onClick={() => handleRemove(idx)}
                    className="text-xs text-red-400 hover:text-red-300 px-1.5 py-1"
                    title={t('حذف البديل', 'Delete option')}
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>

            {/* Collapsed summary line if not editing */}
            {editingIndex !== idx && opt.description && (
              <p className="text-xs text-white/60 line-clamp-1 ps-8">{opt.description}</p>
            )}

            {/* Extended Details Form */}
            {editingIndex === idx && (
              <div className="mt-3 pt-3 border-t border-white/10 space-y-3 text-xs">
                <div>
                  <label className="block text-white/70 mb-1">{t('وصف البديل ونطاق التنفيذ', 'Description & Scope')}</label>
                  <textarea
                    rows={2}
                    disabled={disabled}
                    value={opt.description || ''}
                    onChange={e => handleUpdate(idx, { description: e.target.value })}
                    placeholder={t('شرح موجز لهذا البديل، الخصائص الأساسية ونموذج التسليم', 'Brief description of this option, delivery model, and key capabilities')}
                    className="w-full bg-black/40 border border-white/20 text-white rounded p-2 text-xs"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-emerald-400 font-semibold mb-1">{t('المزايا الرئيسية (مفصولة بفواصل)', 'Key Benefits (comma separated)')}</label>
                    <input
                      type="text"
                      disabled={disabled}
                      value={(opt.benefits || []).join('، ')}
                      onChange={e => handleUpdate(idx, { benefits: e.target.value.split(/[،,]/).map(s => s.trim()).filter(Boolean) })}
                      placeholder={t('ميزة 1، ميزة 2', 'Benefit 1, Benefit 2')}
                      className="w-full bg-black/40 border border-white/20 text-white rounded px-2.5 py-1.5 text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-amber-400 font-semibold mb-1">{t('المخاطر والتحديات (مفصولة بفواصل)', 'Risks (comma separated)')}</label>
                    <input
                      type="text"
                      disabled={disabled}
                      value={(opt.risks || []).join('، ')}
                      onChange={e => handleUpdate(idx, { risks: e.target.value.split(/[،,]/).map(s => s.trim()).filter(Boolean) })}
                      placeholder={t('مخاطرة 1، مخاطرة 2', 'Risk 1, Risk 2')}
                      className="w-full bg-black/40 border border-white/20 text-white rounded px-2.5 py-1.5 text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-sky-400 font-semibold mb-1">{t('شروط النجاح والاعتماد', 'Success Conditions')}</label>
                    <input
                      type="text"
                      disabled={disabled}
                      value={(opt.conditions || []).join('، ')}
                      onChange={e => handleUpdate(idx, { conditions: e.target.value.split(/[،,]/).map(s => s.trim()).filter(Boolean) })}
                      placeholder={t('شرط 1، شرط 2', 'Condition 1, Condition 2')}
                      className="w-full bg-black/40 border border-white/20 text-white rounded px-2.5 py-1.5 text-xs"
                    />
                  </div>
                </div>

                {/* Pre-fill criteria scores if available */}
                {criteria && criteria.length > 0 && (
                  <div className="pt-2 border-t border-white/5">
                    <label className="block text-white/70 font-semibold mb-2">
                      {t('الدرجات المبدئية للمعايير (اختياري - يكملها الذكاء الاصطناعي إن تركت فارغة)', 'Initial Criterion Scores (Optional - AI evaluates if empty)')}
                    </label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
                      {criteria.map(c => {
                        const scoreVal = opt.criterion_scores?.[c.key];
                        return (
                          <div key={c.key} className="p-2 bg-black/30 rounded border border-white/10 text-center">
                            <div className="text-[11px] text-white/60 truncate" title={c.name}>{c.name}</div>
                            <input
                              type="number"
                              min="0"
                              max="100"
                              disabled={disabled}
                              placeholder="—"
                              value={scoreVal !== undefined ? scoreVal : ''}
                              onChange={e => {
                                const val = e.target.value === '' ? undefined : parseFloat(e.target.value);
                                const newScores = { ...(opt.criterion_scores || {}) };
                                if (val === undefined) {
                                  delete newScores[c.key];
                                } else {
                                  newScores[c.key] = val;
                                }
                                handleUpdate(idx, { criterion_scores: newScores });
                              }}
                              className="w-full mt-1 bg-black/60 border border-white/20 text-white text-center font-mono rounded px-1 py-0.5 text-xs"
                            />
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {!disabled && (
        <button
          type="button"
          onClick={handleAdd}
          className="w-full py-2 border-2 border-dashed border-white/20 hover:border-white/40 rounded-xl text-xs font-semibold text-white/80 hover:text-white transition flex items-center justify-center gap-2"
        >
          <span>➕</span>
          {t('إضافة خيار / بديل جديد للمفاضلة', 'Add New Decision Option')}
        </button>
      )}
    </div>
  );
}
