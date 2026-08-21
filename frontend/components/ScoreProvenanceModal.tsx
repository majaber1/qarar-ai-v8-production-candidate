'use client';
import { ScoreProvenance } from '@/lib/api';
import { useLang } from './LanguageProvider';

interface ScoreProvenanceModalProps {
  provenance: ScoreProvenance | null;
  optionTitle?: string;
  onClose: () => void;
  onOpenOverride?: () => void;
}

export default function ScoreProvenanceModal({
  provenance,
  optionTitle,
  onClose,
  onOpenOverride,
}: ScoreProvenanceModalProps) {
  const { t } = useLang();

  if (!provenance) return null;

  const isGate = Boolean(provenance.is_gate);
  const isDisqualified = isGate && !provenance.gate_passed;
  const isHumanOverride = provenance.assessment_source === 'HUMAN';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-white/20 rounded-2xl max-w-2xl w-full p-6 text-white shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-start justify-between gap-3 border-b border-white/10 pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-mono font-bold border border-amber-500/30">
                {optionTitle || provenance.criterion_key}
              </span>
              <span className="text-xs text-white/40">×</span>
              <span className="text-sm font-bold text-white">
                {provenance.criterion_name}
              </span>
              {isHumanOverride && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/30 text-amber-300 font-bold border border-amber-500/40">
                  ✏️ {t('تعديل بشري', 'Human Override')}
                </span>
              )}
            </div>
            <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
              <span>🔍</span>
              {t('سجل الإسناد والتحقق الحسابي', 'Score Provenance & Calculation Audit')}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-white/40 hover:text-white text-xl p-1 rounded-lg hover:bg-white/10 transition"
          >
            ✕
          </button>
        </div>

        {/* Calculation Formula Card */}
        <div className="p-4 rounded-xl bg-black/40 border border-white/10 space-y-3">
          <div className="flex items-center justify-between text-xs text-white/70 border-b border-white/10 pb-2">
            <span>{t('معادلة الحساب الحتمية المعتمدة', 'Deterministic Calculation Formula')}</span>
            <span className="font-mono text-emerald-400">{provenance.assessment_method}</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="p-2.5 rounded-lg bg-white/5 border border-white/10">
              <div className="text-[11px] text-white/50 mb-1">{t('الدرجة الخام', 'Raw Score')}</div>
              <div className="text-xl font-bold font-mono text-white">
                {provenance.raw_score !== null && provenance.raw_score !== undefined ? provenance.raw_score : '—'}
              </div>
              <div className="text-[10px] text-white/40 mt-0.5 font-mono">
                [{provenance.scale_min} - {provenance.scale_max}]
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-white/5 border border-white/10">
              <div className="text-[11px] text-white/50 mb-1">{t('الدرجة المعيارية', 'Normalized')}</div>
              <div className="text-xl font-bold font-mono text-sky-300">
                {provenance.normalized_score !== null && provenance.normalized_score !== undefined ? provenance.normalized_score : '—'}
              </div>
              <div className="text-[10px] text-white/40 mt-0.5">/ 100</div>
            </div>

            <div className="p-2.5 rounded-lg bg-white/5 border border-white/10">
              <div className="text-[11px] text-white/50 mb-1">{t('وزن المعيار', 'Weight')}</div>
              <div className="text-xl font-bold font-mono text-amber-300">
                {provenance.weight_percentage}%
              </div>
              <div className="text-[10px] text-white/40 mt-0.5 font-mono">
                ({provenance.weight})
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-emerald-950/30 border border-emerald-500/30">
              <div className="text-[11px] text-emerald-300/70 mb-1">{t('المساهمة المرجحة', 'Contribution')}</div>
              <div className="text-xl font-bold font-mono text-emerald-400">
                +{provenance.weighted_contribution !== null && provenance.weighted_contribution !== undefined ? provenance.weighted_contribution : '—'}
              </div>
              <div className="text-[10px] text-emerald-300/50 mt-0.5">{t('نقطة في المجموع', 'pts in total')}</div>
            </div>
          </div>

          {/* Direction Note */}
          <div className="text-xs text-white/60 flex items-center gap-1.5 pt-1">
            <span>ℹ️</span>
            <span>
              {provenance.direction === 'lower_better'
                ? t('اتجاه المعيار: الأقل أفضلية (تم عكس الدرجة معيارياً 100 - القيمة)', 'Direction: Lower is better (Normalized as 100 - value)')
                : t('اتجاه المعيار: الأعلى أفضلية', 'Direction: Higher is better')}
            </span>
          </div>
        </div>

        {/* Mandatory Gate Alert (if applicable) */}
        {isGate && (
          <div className={
            isDisqualified
              ? "p-4 rounded-xl border flex items-start gap-3 bg-red-950/30 border-red-500/50 text-red-200"
              : "p-4 rounded-xl border flex items-start gap-3 bg-emerald-950/30 border-emerald-500/40 text-emerald-200"
          }>
            <span className="text-2xl">{isDisqualified ? '⛔' : '🛡️'}</span>
            <div>
              <div className="font-bold text-sm flex items-center gap-2">
                <span>{t('بوابة التأهيل الإلزامية (Mandatory Gate)', 'Mandatory Qualification Gate')}</span>
                <span className={
                  isDisqualified
                    ? "text-[11px] px-2 py-0.5 rounded-full font-bold bg-red-500/30 text-red-300"
                    : "text-[11px] px-2 py-0.5 rounded-full font-bold bg-emerald-500/30 text-emerald-300"
                }>
                  {isDisqualified ? t('غير مستوفٍ - مقصى', 'Disqualified') : t('مستوفٍ للشروط الإلزامية', 'Passed')}
                </span>
              </div>
              <p className="text-xs mt-1 text-white/80">
                {isDisqualified
                  ? provenance.gate_failure_reason || t('لم يحقق البديل الحد الأدنى المطلوب لاجتياز هذه البوابة', 'The option failed the minimum passing threshold for this mandatory gate.')
                  : t('اجتاز البديل العتبة الإلزامية بنجاح.', 'The option successfully met the mandatory threshold.')}
              </p>
            </div>
          </div>
        )}

        {/* Rationale & Evidence Details */}
        <div className="space-y-3">
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-white/50 mb-1.5 flex items-center gap-1.5">
              <span>📝</span>
              {t('تعليل التقييم والحيثيات (Rationale)', 'Assessment Rationale')}
            </h4>
            <p className="p-3 rounded-xl bg-white/5 border border-white/10 text-sm text-white/90 leading-relaxed">
              {provenance.rationale}
            </p>
          </div>

          {/* Evidence Citations & Trust Level */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-white/50 mb-1.5 flex items-center gap-1.5">
              <span>📑</span>
              {t('الأدلة المستندة ومستوى الموثوقية (Evidence & Trust)', 'Evidence References & Trust Level')}
            </h4>
            <div className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex items-center gap-2">
                  <span className={
                    provenance.trust_level === 'A'
                      ? "px-2 py-0.5 rounded font-bold font-mono text-[11px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                      : provenance.trust_level === 'B'
                      ? "px-2 py-0.5 rounded font-bold font-mono text-[11px] bg-sky-500/20 text-sky-300 border border-sky-500/30"
                      : "px-2 py-0.5 rounded font-bold font-mono text-[11px] bg-amber-500/20 text-amber-300 border border-amber-500/30"
                  }>
                    {t('موثوقية الدليل:', 'Trust Level:')} {provenance.trust_level}
                  </span>
                  <span className="text-white/60 font-mono">
                    {t('مستوى الثقة:', 'Confidence:')} {Math.round((provenance.confidence || 0) * 100)}%
                  </span>
                </div>
                <span className="text-[11px] text-white/50">
                  {t('المصدر:', 'Source:')} {provenance.actor} ({provenance.assessment_source})
                </span>
              </div>

              {provenance.evidence_references && provenance.evidence_references.length > 0 && (
                <ul className="text-xs text-white/80 space-y-1 pt-1 border-t border-white/5">
                  {provenance.evidence_references.map((ref, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <span className="text-emerald-400">✓</span>
                      <span>{ref}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Override History (if modified by human) */}
          {provenance.override_history && provenance.override_history.length > 0 && (
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 mb-1.5 flex items-center gap-1.5">
                <span>✏️</span>
                {t('سجل التعديلات البشرية المعتمدة (Override History)', 'Human Review & Override Audit Trail')}
              </h4>
              <div className="space-y-1.5">
                {provenance.override_history.map((ov, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-amber-950/20 border border-amber-500/30 text-xs space-y-1">
                    <div className="flex items-center justify-between text-amber-300 font-semibold">
                      <span>
                        {t('تم تعديل الدرجة من', 'Score modified from')} <b className="font-mono">{ov.previous_score}</b> {t('إلى', 'to')} <b className="font-mono">{ov.new_score}</b>
                      </span>
                      <span className="text-[10px] text-white/50 font-mono">
                        {ov.actor} · {ov.timestamp ? new Date(ov.timestamp).toLocaleString() : ''}
                      </span>
                    </div>
                    <p className="text-white/80 italic">
                      "{ov.reason}"
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Actions */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-4">
          <div className="text-[11px] text-white/40 font-mono">
            {t('تم التدقيق:', 'Audited at:')} {new Date(provenance.timestamp).toLocaleString()}
          </div>
          <div className="flex items-center gap-2">
            {onOpenOverride && (
              <button
                type="button"
                onClick={() => {
                  onClose();
                  onOpenOverride();
                }}
                className="px-4 py-2 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 rounded-xl text-xs font-bold transition flex items-center gap-1.5"
              >
                <span>✏️</span>
                {t('تعديل الدرجة رسمياً (Human Override)', 'Override Score (Human Review)')}
              </button>
            )}
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-semibold transition"
            >
              {t('إغلاق', 'Close')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
