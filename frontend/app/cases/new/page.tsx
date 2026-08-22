'use client';

import { FormEvent, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import DecisionJourney from '@/components/DecisionJourney';
import CriteriaBuilder, { DEFAULT_CRITERIA_PRESET } from '@/components/CriteriaBuilder';
import OptionsEditor from '@/components/OptionsEditor';
import TemplateSelector from '@/components/TemplateSelector';
import { useLang } from '@/components/LanguageProvider';
import { api, DecisionOption, DecisionTemplate, QProject, ScoringCriterion } from '@/lib/api';

const types = [
  ['problem', '⚠', 'حل مشكلة', 'Solve a problem'],
  ['option', '⇄', 'تقييم خيار أو مبادرة', 'Assess an option'],
  ['inquiry', '؟', 'استفسار تنفيذي', 'Executive inquiry'],
];

export default function NewCase() {
  const router = useRouter();
  const { lang, t } = useLang();
  const [type, setType] = useState('problem');
  const [projects, setProjects] = useState<QProject[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  // Form Fields
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [urgency, setUrgency] = useState('medium');
  const [projectId, setProjectId] = useState<string>('');

  // V9 Advanced Criteria & Options
  const [criteria, setCriteria] = useState<ScoringCriterion[]>(DEFAULT_CRITERIA_PRESET);
  const [options, setOptions] = useState<DecisionOption[]>([
    { id: 'A', title: 'الاستمرار بضوابط وتحقق', description: 'الاستمرار في المسار الحالي مع وضع بوابات تحقق دورية.', benefits: ['الاستمرارية وتفادي التوقف'], risks: ['نقص الأدلة التفصيلية'], conditions: ['تحديد المالك المسؤول'], criterion_scores: {} },
    { id: 'B', title: 'مراجعة قصيرة قبل الالتزام', description: 'استكمال الأدلة الحرجة ومراجعة العروض ثم اعتماد القرار.', benefits: ['جودة قرار أعلى ومخاطر أقل'], risks: ['تأخير محدود في الجدول'], conditions: ['جمع أدلة التحقق'], criterion_scores: {} },
    { id: 'C', title: 'إعادة تصميم المسار بالكامل', description: 'إعادة تصميم النطاق والحلول المتأثرة بشكل جذري.', benefits: ['حل جذري مستدام'], risks: ['تكلفة إضافية ووقت أطول'], conditions: ['تأكيد الجدوى الاقتصادية'], criterion_scores: {} },
  ]);

  useEffect(() => {
    api.projects().then(setProjects).catch(() => {});
  }, []);

  const handleApplyTemplate = (tmpl: DecisionTemplate) => {
    setTitle(lang === 'ar' ? tmpl.title_ar : tmpl.title_en);
    setDescription(lang === 'ar' ? tmpl.description_ar : tmpl.description_en);
    if (tmpl.category) setType(tmpl.category);
    if (tmpl.criteria && tmpl.criteria.length > 0) {
      setCriteria(tmpl.criteria);
    }
    if (tmpl.default_options && tmpl.default_options.length > 0) {
      setOptions(tmpl.default_options.map(opt => ({
        id: opt.id,
        title: opt.title,
        description: opt.description,
        benefits: [],
        risks: [],
        conditions: [],
        criterion_scores: {},
      })));
    }
  };

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      const decision = await api.create({
        project_id: projectId ? Number(projectId) : null,
        title: title.trim(),
        description: description.trim(),
        urgency,
        category: type,
        language: lang,
        scoring_criteria: criteria,
        options: options.map(o => ({
          id: o.id,
          title: o.title,
          description: o.description || '',
          benefits: o.benefits || [],
          risks: o.risks || [],
          conditions: o.conditions || [],
          criterion_scores: o.criterion_scores || {},
        })),
      });
      router.push(`/project/${decision.id}`);
    } catch (err: any) {
      setError(err?.message || t('تعذر إنشاء الحالة. تأكد من تسجيل الدخول واتصال النظام.', 'Could not create the case. Check your session and system connection.'));
      setBusy(false);
    }
  }

  return (
    <main className="createFlow container space-y-6">
      <div className="breadcrumb">
        <Link href="/project">{t('مساحة المشغّل', 'Operator workspace')}</Link>
        <span>/</span>
        {t('حالة قرار جديدة', 'New decision case')}
      </div>

      <header className="createHeader space-y-2">
        <span className="pill blue">{t('القرار · الخطوة الأولى', 'Decision · first step')}</span>
        <h1 className="text-2xl font-extrabold text-white">{t('ما القرار الذي تريد اتخاذه؟', 'What decision are you making?')}</h1>
        <p className="text-white/70 text-sm max-w-2xl leading-relaxed">
          {t('ابدأ بالقرار المحدد. سنرشدك لإكمال السياق والبدائل والمعايير والأدلة قبل التحليل الحتمي والمفاضلة الذكية.', 'Start with the specific decision. We will guide you through context, options, criteria, and evidence before deterministic analysis.')}
        </p>
        <DecisionJourney compact />
      </header>

      {/* Decision Template Quick-Start Picker */}
      <section className="card p-4 bg-slate-900/60 border border-white/10 rounded-2xl shadow-xl">
        <TemplateSelector onSelect={handleApplyTemplate} />
      </section>

      <div className="createLayout grid grid-cols-1 lg:grid-cols-3 gap-6">
        <form className="decisionForm lg:col-span-2 space-y-6" onSubmit={submit}>
          {/* Decision Type Buttons */}
          <div className="caseTypeGrid">
            {types.map(item => (
              <button
                type="button"
                aria-pressed={type === item[0]}
                className={type === item[0] ? 'caseType selected' : 'caseType'}
                onClick={() => setType(item[0])}
                key={item[0]}
              >
                <i aria-hidden="true">{item[1]}</i>
                <b>{t(item[2], item[3])}</b>
              </button>
            ))}
          </div>

          {/* Project Association */}
          <div className="field">
            <label>{t('المشروع التابع', 'Project')}</label>
            <select value={projectId} onChange={e => setProjectId(e.target.value)}>
              <option value="">{t('حالة مستقلة بدون مشروع', 'Standalone case')}</option>
              {projects.map(project => (
                <option value={project.id} key={project.id}>{project.name}</option>
              ))}
            </select>
            {!projects.length && (
              <small className="mt-1 block text-amber-400">
                <Link href="/projects/new">{t('أنشئ مشروعًا أولًا', 'Create a project first')} ←</Link>
              </small>
            )}
          </div>

          {/* Title & Description */}
          <div className="field">
            <label>{t('عنوان القرار المختصر والواضح *', 'A short, clear title *')}</label>
            <input
              required
              minLength={3}
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder={t('مثال: اختيار منصة الحوسبة السحابية للمؤسسة', 'e.g. Enterprise Cloud Platform Selection')}
            />
          </div>

          <div className="field">
            <label>{t('شرح الوضع والنتيجة والأهداف المطلوبة *', 'Describe the situation and outcome needed *')}</label>
            <textarea
              required
              minLength={10}
              rows={3}
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder={t('اشرح تفاصيل القرار، النطاق المستهدف، القيود التنظيمية والميزانية التقديرية...', 'Describe the context, constraints, requirements, and desired outcomes...')}
            />
          </div>

          <div className="field">
            <label>{t('درجة الاستعجال والأهمية', 'Urgency')}</label>
            <select value={urgency} onChange={e => setUrgency(e.target.value)}>
              <option value="low">{t('عادية', 'Normal')}</option>
              <option value="medium">{t('مهمة', 'Important')}</option>
              <option value="high">{t('عاجلة', 'Urgent')}</option>
              <option value="critical">{t('حرجة جداً', 'Critical')}</option>
            </select>
          </div>

          {/* Interactive Criteria Builder */}
          <div className="card p-4 bg-black/30 border border-white/10 rounded-xl space-y-3">
            <CriteriaBuilder criteria={criteria} onChange={setCriteria} />
          </div>

          {/* Interactive Options Editor */}
          <div className="card p-4 bg-black/30 border border-white/10 rounded-xl space-y-3">
            <OptionsEditor options={options} criteria={criteria} onChange={setOptions} />
          </div>

          {error && <div className="errorBox p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-red-200 text-xs font-semibold">{error}</div>}

          <div className="formActions flex items-center justify-between border-t border-white/10 pt-4">
            <Link className="btn secondary" href="/project">
              {t('إلغاء', 'Cancel')}
            </Link>
            <button className="btn primary" disabled={busy}>
              {busy ? t('جارٍ الإنشاء...', 'Creating...') : t('إنشاء الحالة وبدء التحليل', 'Create case & proceed')}
            </button>
          </div>
        </form>

        <aside className="createHelp space-y-4">
          <div className="card p-4 bg-white/5 border border-white/10 rounded-xl space-y-3">
            <b className="text-sm font-bold text-white block">{t('ماذا يحدث في نظام قرار V9؟', 'How Qarar V9 Works')}</b>
            <ol className="space-y-2 text-xs text-white/70 list-decimal list-inside leading-relaxed">
              <li>{t('تحديد المعايير والبوابات الإلزامية التي تقصي الخيارات غير المستوفية.', 'Configure criteria & mandatory qualification gates that filter ineligible options.')}</li>
              <li>{t('تحليل الأدلة والوثائق عبر Knowledge Fabric واستخراج درجات معللة.', 'Knowledge Fabric analyzes evidence and assigns justified provenance scores.')}</li>
              <li>{t('حساب الترتيب الحتمي والتحقق من سيناريوهات الأعمال الخمسة.', 'Authoritative Python engine computes deterministic ranking & 5 business scenarios.')}</li>
              <li>{t('إمكانية التعديل البشري المسبب ومراجعة مجلس القرار والاعتماد.', 'Audited human overrides and executive approval workflow.')}</li>
            </ol>
          </div>

          <div className="card p-4 bg-amber-950/20 border border-amber-500/30 rounded-xl text-xs space-y-2">
            <span className="font-bold text-amber-300 flex items-center gap-1.5">
              <span>💡</span>
              {t('ميزة إسناد الدرجات (Provenance)', 'Score Provenance Guarantee')}
            </span>
            <p className="text-white/80 leading-relaxed">
              {t('كل درجة في مصفوفة التقييم قابلة للتدقيق والتفسير الكامل لمعرفة مصدرها والأدلة المرتبطة بها والمعادلة الحسابية المعتمدة.', 'Every cell in the matrix is fully traceable to its cited evidence, trust rating, and mathematical formula.')}
            </p>
          </div>
        </aside>
      </div>
    </main>
  );
}
