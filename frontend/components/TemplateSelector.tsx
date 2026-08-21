'use client';
import { useEffect, useState } from 'react';
import { api, DecisionTemplate } from '@/lib/api';
import { useLang } from './LanguageProvider';

interface TemplateSelectorProps {
  onSelect: (template: DecisionTemplate) => void;
}

export default function TemplateSelector({ onSelect }: TemplateSelectorProps) {
  const { t, lang } = useLang();
  const [templates, setTemplates] = useState<DecisionTemplate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.templates()
      .then(setTemplates)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-xs text-white/50 animate-pulse text-center">
        {t('جارٍ تحميل القوالب الجاهزة...', 'Loading decision templates...')}
      </div>
    );
  }

  if (!templates || templates.length === 0) return null;

  return (
    <div className="templateSelector space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-white/70 uppercase tracking-wider flex items-center gap-1.5">
          <span>📑</span>
          {t('أو ابدأ باستخدام أحد قوالب القرارات الخمسة الجاهزة', 'Or start with a pre-configured Decision Template')}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2.5">
        {templates.map(tmpl => {
          const title = lang === 'ar' ? tmpl.title_ar : tmpl.title_en;
          const desc = lang === 'ar' ? tmpl.description_ar : tmpl.description_en;

          return (
            <div
              key={tmpl.id}
              className="p-3.5 rounded-xl border border-white/10 bg-white/5 hover:border-amber-500/50 hover:bg-white/10 transition flex flex-col justify-between gap-3 text-start group"
            >
              <div className="space-y-1.5">
                <div className="text-[11px] font-mono text-amber-400/80 uppercase font-semibold">
                  {tmpl.category}
                </div>
                <h4 className="font-bold text-sm text-white group-hover:text-amber-300 transition line-clamp-2">
                  {title}
                </h4>
                <p className="text-[11px] text-white/60 line-clamp-3 leading-relaxed">
                  {desc}
                </p>
              </div>

              <div className="space-y-2 pt-2 border-t border-white/5">
                <div className="flex items-center justify-between text-[10px] text-white/50 font-mono">
                  <span>{tmpl.criteria?.length || 0} {t('معايير', 'criteria')}</span>
                  <span>{tmpl.default_options?.length || 0} {t('بدائل', 'options')}</span>
                </div>
                <button
                  type="button"
                  onClick={() => onSelect(tmpl)}
                  className="w-full py-1.5 px-3 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 rounded-lg text-xs font-bold transition"
                >
                  {t('استخدام هذا القالب', 'Use Template')}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
