'use client';
import { useState } from 'react';
import { api, QCase, ScoreProvenance } from '@/lib/api';
import { useLang } from './LanguageProvider';

interface ScoreOverrideModalProps {
  caseId: string;
  provenance: ScoreProvenance | null;
  optionTitle?: string;
  onSuccess: (updatedCase: QCase) => void;
  onClose: () => void;
}

export default function ScoreOverrideModal({
  caseId,
  provenance,
  optionTitle,
  onSuccess,
  onClose,
}: ScoreOverrideModalProps) {
  const { t } = useLang();
  const [newScore, setNewScore] = useState<number>(provenance?.raw_score ?? 80);
  const [reason, setReason] = useState<string>('');
  const [busy, setBusy] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  if (!provenance) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason || reason.trim().length < 3) {
      setError(t('يجب كتابة مبرر موضوعي للتعديل (3 أحرف على الأقل)', 'Please provide a mandatory justification (min 3 chars)'));
      return;
    }
    setBusy(true);
    setError('');
    try {
      const updated = await api.overrideScore(caseId, {
        option_id: (provenance as any).option_id || provenance.criterion_key,
        criterion_key: provenance.criterion_key,
        new_score: newScore,
        reason: reason.trim(),
      });
      onSuccess(updated);
      onClose();
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-amber-500/40 rounded-2xl max-w-lg w-full p-6 text-white shadow-2xl space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-white/10 pb-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">
                {optionTitle || (provenance as any).option_id}
              </span>
              <span className="text-sm font-semibold text-white/80">
                {provenance.criterion_name}
              </span>
            </div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>✏️</span>
              {t('تعديل بشري رسمي للدرجة (Score Override)', 'Human Review Score Override')}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-white/40 hover:text-white text-xl p-1 rounded-lg hover:bg-white/10 transition"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-red-200 text-xs font-semibold">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {/* Current vs New Score */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-center">
              <label className="block text-white/50 mb-1">{t('الدرجة الحالية (الذكاء الاصطناعي)', 'Current Score (AI)')}</label>
              <div className="text-xl font-bold font-mono text-white/70">
                {provenance.raw_score !== null && provenance.raw_score !== undefined ? provenance.raw_score : '—'}
              </div>
              <div className="text-[10px] text-white/40 mt-0.5">
                [{provenance.scale_min} - {provenance.scale_max}]
              </div>
            </div>

            <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 text-center">
              <label className="block text-amber-300 font-bold mb-1">{t('الدرجة الجديدة المعدلة', 'New Override Score')}</label>
              <input
                type="number"
                required
                min={provenance.scale_min}
                max={provenance.scale_max}
                step="0.5"
                value={newScore}
                onChange={e => setNewScore(parseFloat(e.target.value) || 0)}
                className="w-full bg-black/60 border border-amber-500/50 text-amber-300 font-mono font-bold text-center text-xl rounded p-1 focus:outline-none focus:ring-1 focus:ring-amber-400"
              />
              <div className="text-[10px] text-white/40 mt-0.5">
                {t('ضمن المقياس المحدد', 'Within scale range')}
              </div>
            </div>
          </div>

          {/* Mandatory Reason */}
          <div>
            <label className="block text-white/90 font-bold mb-1.5">
              {t('المبرر الموضوعي للتعديل (إلزامي للتدقيق والامتثال) *', 'Mandatory Justification / Rationale (Audit Trail) *')}
            </label>
            <textarea
              required
              rows={3}
              value={reason}
              onChange={e => setReason(e.target.value)}
              placeholder={t('اكتب بالتفصيل سبب تعديل الدرجة (مثال: تم الحصول على خصم حكومي خاص أو شهادة ترخيص إضافية)', 'Provide full justification (e.g. verified new discount, validated audit certification, or special concession)')}
              className="w-full bg-black/40 border border-white/20 text-white rounded-xl p-3 text-xs focus:outline-none focus:border-amber-400 leading-relaxed"
            />
          </div>

          {/* Warning Notice */}
          <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-amber-200 text-[11px] flex items-start gap-2">
            <span>⚠️</span>
            <span>
              {t('سيؤدي هذا الإجراء إلى إعادة حساب الترتيب الحتمي ومصفوفة الحساسية فوراً وتسجيل المبرر في سجل تدقيق القضية.', 'This action will instantly recalculate deterministic rankings and sensitivity matrix, recording your reason in the permanent audit trail.')}
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-2 border-t border-white/10 pt-3">
            <button
              type="button"
              disabled={busy}
              onClick={onClose}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl font-semibold transition"
            >
              {t('إلغاء', 'Cancel')}
            </button>
            <button
              type="submit"
              disabled={busy}
              className="px-5 py-2 bg-amber-500 hover:bg-amber-400 text-black font-bold rounded-xl shadow-lg transition flex items-center gap-1.5"
            >
              {busy ? (
                <span>{t('جارٍ الحفظ...', 'Saving...')}</span>
              ) : (
                <>
                  <span>✓</span>
                  <span>{t('تأكيد التعديل وإعادة الحساب', 'Confirm Override & Recalculate')}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
