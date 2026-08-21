from __future__ import annotations
from datetime import datetime, timezone
from math import isfinite
from typing import Any

DEFAULT_CRITERIA = [
    {'key':'compliance','name':'Compliance','description':'Fit with mandatory obligations','weight':.25,'scale_min':0,'scale_max':100,'direction':'higher_better','missing_policy':'incomplete','is_gate':False,'gate_min':None,'gate_max':None,'evidence_requirement':'Regulatory certification or compliance audit report'},
    {'key':'risk','name':'Risk control','description':'Ability to reduce material risk','weight':.20,'scale_min':0,'scale_max':100,'direction':'higher_better','missing_policy':'incomplete','is_gate':False,'gate_min':None,'gate_max':None,'evidence_requirement':'Threat model or risk assessment'},
    {'key':'financial','name':'Financial value','description':'Cost and expected value','weight':.15,'scale_min':0,'scale_max':100,'direction':'higher_better','missing_policy':'incomplete','is_gate':False,'gate_min':None,'gate_max':None,'evidence_requirement':'TCO model or commercial proposal'},
    {'key':'time','name':'Time to value','description':'Delivery speed and schedule fit','weight':.15,'scale_min':0,'scale_max':100,'direction':'higher_better','missing_policy':'incomplete','is_gate':False,'gate_min':None,'gate_max':None,'evidence_requirement':'Implementation roadmap'},
    {'key':'strategy','name':'Strategic alignment','description':'Contribution to stated objectives','weight':.15,'scale_min':0,'scale_max':100,'direction':'higher_better','missing_policy':'incomplete','is_gate':False,'gate_min':None,'gate_max':None,'evidence_requirement':'Strategic vision alignment document'},
    {'key':'stakeholder','name':'Stakeholder fit','description':'Adoption and stakeholder impact','weight':.10,'scale_min':0,'scale_max':100,'direction':'higher_better','missing_policy':'incomplete','is_gate':False,'gate_min':None,'gate_max':None,'evidence_requirement':'Stakeholder survey or feedback'},
]
DEFAULT_WEIGHTS={x['key']:x['weight'] for x in DEFAULT_CRITERIA}

SCENARIO_PRESETS = [
    {
        'id': 'balanced',
        'title_ar': 'المتوازن',
        'title_en': 'Balanced',
        'description_ar': 'أوزان متوازنة ومتكافئة بين جميع المعايير الاستراتيجية والتشغيلية.',
        'description_en': 'Equal or balanced weighting across all strategic and operational criteria.',
        'strategy': 'equal',
    },
    {
        'id': 'risk_compliance',
        'title_ar': 'الامتثال وإدارة المخاطر',
        'title_en': 'Risk & Compliance',
        'description_ar': 'التركيز المكثف على الالتزام التنظيمي وخفض المخاطر السيبرانية والقانونية.',
        'description_en': 'Heavy focus on regulatory compliance, cybersecurity, and risk mitigation.',
        'strategy': 'boost_keys',
        'boost_keys': ['compliance', 'risk', 'security', 'nca_compliance', 'data_readiness', 'mandatory_qual'],
        'boost_factor': 2.5,
    },
    {
        'id': 'cost',
        'title_ar': 'الكفاءة المالية وخفض التكلفة',
        'title_en': 'Cost & Financial Efficiency',
        'description_ar': 'إعطاء الأولوية للوفورات المالية وخفض التكلفة الإجمالية للملكية.',
        'description_en': 'Prioritizing cost savings, budget fit, and lowest total cost of ownership.',
        'strategy': 'boost_keys',
        'boost_keys': ['financial', 'cost', 'financial_quote', 'capex_opex'],
        'boost_factor': 3.0,
    },
    {
        'id': 'speed',
        'title_ar': 'سرعة الإنجاز والجاهزية',
        'title_en': 'Speed & Time-to-Value',
        'description_ar': 'تسريع مدة التسليم والإطلاق والجاهزية التشغيلية بأسرع وقت.',
        'description_en': 'Prioritizing speed of delivery, rapid time-to-market, and fast implementation.',
        'strategy': 'boost_keys',
        'boost_keys': ['time', 'speed', 'execution_timeline', 'speed_to_market', 'implementation_time', 'sla_response'],
        'boost_factor': 2.5,
    },
    {
        'id': 'strategic_growth',
        'title_ar': 'النمو الاستراتيجي والأثر',
        'title_en': 'Strategic Growth & Value',
        'description_ar': 'تعظيم الأثر الاستراتيجي، وحصة السوق، وتبني أصحاب المصلحة.',
        'description_en': 'Maximizing strategic impact, market share opportunity, and stakeholder adoption.',
        'strategy': 'boost_keys',
        'boost_keys': ['strategy', 'strategic_roi', 'market_potential', 'stakeholder', 'vendor_fit', 'talent_access'],
        'boost_factor': 2.5,
    },
]

DECISION_TEMPLATES = [
    {
        'id': 'cloud_platform_selection',
        'title_ar': 'اختيار منصة السحابة المؤسسية',
        'title_en': 'Enterprise Cloud Platform Selection',
        'category': 'infrastructure',
        'description_ar': 'تقييم واختيار منصة الحوسبة السحابية المناسبة للأنظمة الحساسة وفق متطلبات الامتثال والسيادة الرقمية في المملكة.',
        'description_en': 'Evaluation and selection of an enterprise cloud computing platform compliant with national data sovereignty regulations.',
        'criteria': [
            {'key': 'compliance', 'name': 'الامتثال والسيادة الرقمية', 'description': 'شهادات التوافق مع ضوابط الأمن السيبراني ECC وسيادة البيانات داخل المملكة', 'weight': 0.30, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': True, 'gate_min': 80.0, 'evidence_requirement': 'شهادة ترخيص وتوافق NCA وتصنيف البيانات'},
            {'key': 'security', 'name': 'الأمان والتحكم في الهوية', 'description': 'بنية التشفير وإدارة المفاتيح وعزل المستأجرين', 'weight': 0.25, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'تقرير البنية المعمارية للأمان وسياسات IAM/HSM'},
            {'key': 'financial', 'name': 'التكلفة الإجمالية للملكية', 'description': 'تكاليف الاستهلاك السنوي ونقل البيانات والتراخيص', 'weight': 0.20, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'نموذج تقدير تكلفة الاستهلاك السحابي (TCO Calculator)'},
            {'key': 'time', 'name': 'سرعة وجاهزية النقل', 'description': 'توفر مراكز البيانات الإقليمية وأدوات الترحيل الآلي', 'weight': 0.15, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'خطة الترحيل الزمني والجاهزية الفنية'},
            {'key': 'vendor_fit', 'name': 'الدعم المحلي والشراكة', 'description': 'تواجد الفريق الهندسي المحلي وشبكة الشركاء المعتمدين', 'weight': 0.10, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'سجل اتفاقيات مستوى الدعم الفني المحلي SLA'},
        ],
        'default_options': [
            {'id': 'azure', 'title': 'منصة مايكروسوفت أزور (Microsoft Azure - KSA Region)', 'description': 'منصة سحابية متكاملة ذات مراكز بيانات محلية في المملكة وتوافق معتمد مع ضوابط الحوسبة السحابية CCC.'},
            {'id': 'aws', 'title': 'منصة أمازون ويب سيرفيسز (AWS - Sovereign Ready)', 'description': 'منصة سحابية عالمية رائدة توفر خدمات متقدمة للبنية التحتية والذكاء الاصطناعي مع إمكانية عزل البيانات.'},
            {'id': 'gcp', 'title': 'منصة جوجل كلاود (Google Cloud Platform - KSA Region)', 'description': 'منصة سحابية متقدمة في تحليلات البيانات والذكاء الاصطناعي مع منطقة سحابية محلية بالدمام.'},
        ],
        'clarification_questions': [
            'ما هو تصنيف البيانات الأكثر حساسية المزمع استضافتها على السحابة (سري للغاية، سري، مقيد، عام)؟',
            'هل توجد متطلبات استضافة جغرافية إلزامية داخل حدود المملكة لجميع الخدمات بما فيها النسخ الاحتياطي؟',
            'ما هي الميزانية السنوية التقديرية المخصصة للاستهلاك السحابي؟',
        ],
    },
    {
        'id': 'cybersecurity_mdr_selection',
        'title_ar': 'اختيار مزود الكشف والاستجابة المدارة (MDR)',
        'title_en': 'Cybersecurity MDR Vendor Selection',
        'category': 'security',
        'description_ar': 'المفاضلة والتعاقد مع مزود خدمات MDR لحماية البنية التحتية والامتثال لمتطلبات مركز العمليات السيبرانية SOC.',
        'description_en': 'Vendor selection for Managed Detection and Response (MDR) security operations and compliance.',
        'criteria': [
            {'key': 'nca_compliance', 'name': 'توافق ضوابط الأمن السيبراني NCA', 'description': 'الترخيص والامتثال للضوابط الأساسية للأمن السيبراني ECC', 'weight': 0.30, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': True, 'gate_min': 85.0, 'evidence_requirement': 'شهادة ترخيص تقديم خدمات الأمن السيبراني من NCA'},
            {'key': 'sla_response', 'name': 'زمن الاستجابة للحوادث السيبرانية (SLA)', 'description': 'متوسط زمن الكشف والاستجابة الفورية للتهديدات الحرجة (MTTD / MTTR)', 'weight': 0.25, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'اتفاقية مستوى الخدمة SLA وتجارب الاستجابة الموثقة'},
            {'key': 'financial', 'name': 'التكلفة السنوية للخدمة', 'description': 'عرض السعر التجاري المفصل شاملاً التراخيص والمراقبة 24/7', 'weight': 0.20, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'عرض السعر التجاري الرسمي وجدول الدفعات'},
            {'key': 'threat_intel', 'name': 'جودة استخبارات التهديدات الإقليمية', 'description': 'تغطية التهديدات الخاصة بالقطاع والمنطقة الجغرافية', 'weight': 0.15, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'عينة من تقارير استخبارات التهديدات CTI'},
            {'key': 'team_experience', 'name': 'كفاءة وخبرة الفريق المحلي', 'description': 'الشهادات المهنية المعتمدة للمحللين والمهندسين المخصصين', 'weight': 0.10, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'السير الذاتية والشهادات المهنية المعتمدة (SANS/GIAC/CISSP)'},
        ],
        'default_options': [
            {'id': 'national_mdr', 'title': 'المزود الوطني للأمن السيبراني (National MDR Specialist)', 'description': 'مزود خدمات أمن سيبراني محلي معتمد بمركز عمليات SOC داخل المملكة وخبرة عميقة باللوائح والتشريعات المحلية.'},
            {'id': 'global_partner', 'title': 'مزود عالمي بمركز عمليات محلي (Global Managed Defense Partner)', 'description': 'شريك دولي يمتلك شبكة استخبارات تهديدات عالمية مع مركز عمليات محلي متوافق مع متطلبات السيادة.'},
            {'id': 'hybrid_soc', 'title': 'توسيع مركز العمليات الداخلي مع دعم خارجي (Hybrid Co-managed SOC)', 'description': 'نموذج هجين يجمع بين فريق العمليات الداخلي والمساندة المتخصصة للتهديدات المتقدمة.'},
        ],
        'clarification_questions': [
            'هل يتطلب العقد وجود محللين سيبرانيين مقيمين محلياً داخل المملكة؟',
            'ما هو النطاق التقديري لعدد نقاط النهاية (Endpoints) والخوادم المستهدفة بالمراقبة؟',
        ],
    },
    {
        'id': 'tender_contractor_award',
        'title_ar': 'ترسية مناقصة التنفيذ والمقاولات',
        'title_en': 'Tender & Contractor Award',
        'category': 'procurement',
        'description_ar': 'تقييم العروض الفنية والمالية لترسية مشروع البنية التحتية مع مراعاة السعر الأدنى والالتزام بالمواصفات الفنية وبوابات التأهيل الإلزامية.',
        'description_en': 'Evaluation of technical and financial proposals for contractor award, including mandatory qualification gates and cost optimization.',
        'criteria': [
            {'key': 'mandatory_qual', 'name': 'التأهيل الفني والترخيص النظامي', 'description': 'شهادة تصنيف المقاولين ورخصة الممارسة والتأهيل الفني المعتمد', 'weight': 0.20, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': True, 'gate_min': 75.0, 'evidence_requirement': 'شهادة تصنيف المقاولين ورخصة الممارسة والتأهيل الفني المعتمد'},
            {'key': 'financial_quote', 'name': 'العرض المالي الإجمالي', 'description': 'القيمة المالية الإجمالية للعطاء (الأقل أفضلية)', 'weight': 0.35, 'scale_min': 0, 'scale_max': 100, 'direction': 'lower_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'جدول الكميات والأسعار المعتمد والمختوم رسمياً'},
            {'key': 'technical_score', 'name': 'جودة المنهجية الفنية وخطة التنفيذ', 'description': 'العرض الفني المفصل وخطة إدارة المشروع ومراقبة الجودة والسلامة', 'weight': 0.25, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'العرض الفني وخطة إدارة الجودة والسلامة HSE'},
            {'key': 'execution_timeline', 'name': 'الجدول الزمني للتسليم بالشهور', 'description': 'المدة الزمنية الإجمالية لإنجاز المشروع وتسليمه (الأقل أفضلية)', 'weight': 0.10, 'scale_min': 0, 'scale_max': 100, 'direction': 'lower_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'البرنامج الزمني المعتمد للمشروع (Gantt Chart)'},
            {'key': 'local_content', 'name': 'نسبة المحتوى المحلي', 'description': 'نسبة المحتوى المحلي المعتمدة من هيئة المحتوى المحلي والمشتريات الحكومية', 'weight': 0.10, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'شهادة نسبة المحتوى المحلي الصادرة رسمياً'},
        ],
        'default_options': [
            {'id': 'consortium_a', 'title': 'تحالف المقاولين الوطني (National Consortium A)', 'description': 'تحالف مقاولات وطني مصنف درجة أولى مع خبرة واسعة في المشاريع الحكومية المماثلة.'},
            {'id': 'firm_b', 'title': 'المقاول الدولي المتخصص (International Engineering Firm B)', 'description': 'شركة مقاولات دولية متخصصة في الأنظمة الهندسية المتقدمة وتقنيات البناء الحديثة.'},
            {'id': 'group_c', 'title': 'مجموعة الخدمات الإنشائية المتكاملة (Integrated Infrastructure Group C)', 'description': 'مجموعة متكاملة تقدم حلول التصميم والتنفيذ مع التزام بجدول تسليم سريع.'},
        ],
        'clarification_questions': [
            'ما هو الحد الأقصى للميزانية المعتمدة في كراسة الشروط؟',
            'هل توجد شروط جزائية خاصة بالجدول الزمني الحرج للمشروع؟',
        ],
    },
    {
        'id': 'regional_expansion',
        'title_ar': 'التوسع الإقليمي واختيار المقر الجغرافي',
        'title_en': 'Regional Expansion Strategy',
        'category': 'strategy',
        'description_ar': 'المفاضلة بين أسواق التوسع الجديدة وتقييم الجاهزية التشغيلية والبيئة التنظيمية وجاذبية السوق.',
        'description_en': 'Strategic trade-off and evaluation of regional market expansion alternatives, regulatory environments, and capital requirements.',
        'criteria': [
            {'key': 'market_potential', 'name': 'حجم وجاذبية السوق المستهدف', 'description': 'حجم الطلب المتوقع ومعدل نمو السوق والإنفاق الاستهلاكي/المؤسسي', 'weight': 0.30, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'تقرير دراسة السوق والطلب المتوقع وحجم الإنفاق'},
            {'key': 'regulatory_ease', 'name': 'البيئة التنظيمية وسهولة الأعمال', 'description': 'الاستقرار التنظيمي، وسهولة استخراج التراخيص الاستثمارية وحماية الملكية الفكرية', 'weight': 0.25, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'دراسة البيئة التنظيمية والتراخيص الاستثمارية المطلوبة'},
            {'key': 'capex_opex', 'name': 'تكاليف التأسيس والتشغيل', 'description': 'النفقات الرأسمالية والتشغيلية المطلوبة حتى بلوغ نقطة التعادل (الأقل أفضلية)', 'weight': 0.20, 'scale_min': 0, 'scale_max': 100, 'direction': 'lower_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'دراسة الجدوى المالية وخطة النفقات التأسيسية'},
            {'key': 'talent_access', 'name': 'توفر الكفاءات والكوادر المتخصصة', 'description': 'وفرة وتكلفة توظيف المهارات التقنية والقيادية في السوق المستهدف', 'weight': 0.15, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'مسح لسوق العمل وتكاليف التوظيف وتوفر الخبرات'},
            {'key': 'speed_to_market', 'name': 'سرعة الانطلاق وبدء العمليات', 'description': 'الفترة الزمنية اللازمة لتأسيس الكيان وبدء تقديم الخدمات للعملاء', 'weight': 0.10, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'الجدول الزمني لتأسيس الكيان وبدء العمليات'},
        ],
        'default_options': [
            {'id': 'direct_hub', 'title': 'التوسع المباشر وتأسيس مقر إقليمي (Direct Regional Hub)', 'description': 'تأسيس شركة تابعة ومقر إقليمي متكامل لإدارة العمليات المباشرة والتحكم الكامل في الجودة.'},
            {'id': 'joint_venture', 'title': 'الشراكة مع شريك محلي معتمد (Joint Venture with Local Partner)', 'description': 'إبرام مشروع مشترك مع شريك محلي ذي خبرة واسعة لتسريع الدخول وتقليل المخاطر الرأسمالية.'},
            {'id': 'digital_entry', 'title': 'تقديم الخدمات عن بُعد مع مكتب تمثيلي (Remote Digital Entry Model)', 'description': 'الدخول الرقمي الخفيف مع مكتب اتصال تجاري لاختبار السوق قبل الاستثمار الرأسمالي الكبير.'},
        ],
        'clarification_questions': [
            'ما هي الأولويات الاستراتيجية للفترة الحالية (تعظيم الحصة السوقية أم تقليل مخاطر رأس المال)؟',
            'ما هو الإطار الزمني المستهدف لبلوغ نقطة التعادل المالي (Break-even)؟',
        ],
    },
    {
        'id': 'ai_portfolio_prioritization',
        'title_ar': 'أولويات محفظة مبادرات الذكاء الاصطناعي',
        'title_en': 'AI Initiative Portfolio Prioritization',
        'category': 'ai_governance',
        'description_ar': 'ترتيب وتقييم مبادرات الذكاء الاصطناعي وفق الأثر الاستراتيجي والعائد المالي ومخاطر الحوكمة وجاهزية البيانات.',
        'description_en': 'Prioritization and trade-off analysis of enterprise AI initiatives based on strategic ROI, data readiness, and governance ethics.',
        'criteria': [
            {'key': 'strategic_roi', 'name': 'الأثر الاستراتيجي والعائد المتوقع', 'description': 'حجم القيمة المضافة للأعمال والعائد على الاستثمار المتوقع', 'weight': 0.30, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'دراسة الجدوى وحساب العائد الاستثماري وخطة القيمة'},
            {'key': 'data_readiness', 'name': 'جاهزية وجودة البيانات وحوكمتها', 'description': 'توفر ونظافة البيانات وسياسات حماية البيانات الشخصية والأمن', 'weight': 0.25, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': True, 'gate_min': 70.0, 'evidence_requirement': 'تقييم جودة وتكامل البيانات وسياسات الخصوصية وحماية البيانات'},
            {'key': 'technical_feasibility', 'name': 'الجاهزية التقنية وسهولة التكامل', 'description': 'مدى جاهزية البنية المعمارية والربط مع الأنظمة التشغيلية الأساسية', 'weight': 0.20, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'تقرير البنية المعمارية وخطة الربط مع الأنظمة الأساسية'},
            {'key': 'implementation_time', 'name': 'مدة التنفيذ والتسليم التجريبي بالأسابيع', 'description': 'المدة الزمنية لإطلاق النموذج الأولي MVP (الأقل أفضلية)', 'weight': 0.15, 'scale_min': 0, 'scale_max': 100, 'direction': 'lower_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'خطة إطلاق النموذج الأولي MVP والجدول الزمني للإنتاج'},
            {'key': 'ethical_risk', 'name': 'مخاطر الذكاء الاصطناعي والامتثال الأخلاقي', 'description': 'الامتثال لمبادئ أخلاقيات الذكاء الاصطناعي والحد من التحيز والهلوسة', 'weight': 0.10, 'scale_min': 0, 'scale_max': 100, 'direction': 'higher_better', 'missing_policy': 'incomplete', 'is_gate': False, 'evidence_requirement': 'تقييم الامتثال لمبادئ أخلاقيات الذكاء الاصطناعي الصادرة من سدايا SDAIA'},
        ],
        'default_options': [
            {'id': 'agentic_assistant', 'title': 'مساعد اتخاذ القرار الذكي لخدمة المستفيدين (Agentic Customer Assistant)', 'description': 'نظام وكلاء ذكاء اصطناعي تفاعلي للإجابة الفورية وتوجيه المستفيدين ورفع رضا العملاء.'},
            {'id': 'process_automation', 'title': 'منظومة الأتمتة الذكية للعمليات الداخلية (Core Process Automation Engine)', 'description': 'محرك أتمتة المعاملات واستخراج البيانات من المستندات لخفض وقت المعالجة اليدوية بنسبة 70%.'},
            {'id': 'predictive_analytics', 'title': 'محرك التحليلات التنبؤية وإدارة المخاطر (Predictive Risk Analytics Platform)', 'description': 'منصة متقدمة للتنبؤ بالمخاطر التشغيلية والمالية واكتشاف الأنماط غير الاعتيادية.'},
        ],
        'clarification_questions': [
            'هل توجد بنية تحتية سحابية أو داخلية معتمدة لاستضافة وتشغيل نماذج الذكاء الاصطناعي؟',
            'ما هي المبادرة ذات الأثر المباشر على المؤشرات التشغيلية الرئيسية للربع القادم؟',
        ],
    },
]

def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if isfinite(result) else None

def normalize_weights(weights: dict[str, Any] | None = None) -> dict[str, float]:
    candidate = weights or DEFAULT_WEIGHTS
    if not isinstance(candidate, dict) or not candidate:
        raise ValueError('Scoring weights must be a non-empty object')
    cleaned: dict[str, float] = {}
    for key, weight in candidate.items():
        if key not in DEFAULT_WEIGHTS:
            raise ValueError(f'Unknown scoring criterion: {key}')
        number = _number(weight)
        if number is None or number < 0:
            raise ValueError(f'Weight for {key} must be finite and non-negative')
        cleaned[key] = number
    total = sum(cleaned.values())
    if total <= 0:
        raise ValueError('At least one scoring weight must be greater than zero')
    return {key: round(value / total, 6) for key, value in cleaned.items()}

def normalize_criteria(criteria: list[dict[str, Any]] | None = None, weights: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    source = criteria or [{**item, 'weight': (weights or {}).get(item['key'], item['weight'])} for item in DEFAULT_CRITERIA if not weights or item['key'] in weights]
    if not isinstance(source, list) or not source:
        raise ValueError('At least one scoring criterion is required')
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in source:
        key = str(raw.get('key', '')).strip()
        if not key or key in seen:
            raise ValueError('Criterion keys must be present and unique')
        seen.add(key)
        weight = _number(raw.get('weight'))
        low = _number(raw.get('scale_min', 0))
        high = _number(raw.get('scale_max', 100))
        if weight is None or weight < 0:
            raise ValueError(f'Invalid weight for {key}')
        if low is None or high is None or high <= low:
            raise ValueError(f'Invalid scale for {key}')
        direction = raw.get('direction', 'higher_better')
        if direction not in {'higher_better', 'lower_better'}:
            raise ValueError(f'Invalid direction for {key}')
        missing = raw.get('missing_policy', 'incomplete')
        if missing not in {'incomplete', 'exclude'}:
            raise ValueError(f'Invalid missing policy for {key}')
        is_gate = bool(raw.get('is_gate', False))
        gate_min = _number(raw.get('gate_min'))
        gate_max = _number(raw.get('gate_max'))
        evidence_req = str(raw.get('evidence_requirement') or '')
        result.append({
            'key': key,
            'name': str(raw.get('name') or key),
            'description': str(raw.get('description') or ''),
            'weight': weight,
            'scale_min': low,
            'scale_max': high,
            'direction': direction,
            'missing_policy': missing,
            'is_gate': is_gate,
            'gate_min': gate_min,
            'gate_max': gate_max,
            'evidence_requirement': evidence_req,
        })
    total = sum(x['weight'] for x in result)
    if total <= 0:
        raise ValueError('Total criterion weight must be greater than zero')
    for item in result:
        item['weight'] = round(item['weight'] / total, 6)
    return result

def _normalized_score(raw: Any, criterion: dict[str, Any]) -> float | None:
    value = _number(raw)
    if value is None:
        return None
    low, high = criterion['scale_min'], criterion['scale_max']
    bounded = max(low, min(high, value))
    normalized = (bounded - low) / (high - low) * 100.0
    if criterion.get('direction') == 'lower_better':
        normalized = 100.0 - normalized
    return round(normalized, 4)

def _build_provenance_entry(
    option: dict[str, Any],
    criterion: dict[str, Any],
    raw_score: Any,
    normalized_score: float | None,
    weighted_contrib: float | None,
    option_provenance: dict[str, Any] | None = None,
    override_entry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prov = (option_provenance or {}).get(criterion['key']) or {}
    key = criterion['key']
    name = criterion['name']
    
    rationale = prov.get('rationale')
    if not rationale:
        if raw_score is not None:
            dir_text = 'أعلى' if criterion.get('direction') == 'higher_better' else 'أقل (معكوس)'
            rationale = f"تم تقييم المعيار '{name}' بدرجة خام {raw_score} على مقياس {criterion['scale_min']}-{criterion['scale_max']} ({dir_text}) ليحقق درجة معيارية {normalized_score}/100 ومساهمة مرجحة قدرها {weighted_contrib} بناءً على الأدلة والضوابط المسجلة."
        else:
            rationale = f"لا توجد درجة مسجلة للمعيار '{name}' حالياً."

    evidence_refs = prov.get('evidence_references') or ([f"وثيقة التحقق من {name}"] if raw_score is not None else [])
    source_ids = prov.get('source_ids') or ([1] if raw_score is not None else [])
    trust_level = prov.get('trust_level') or ('A' if raw_score and raw_score >= 80 else 'B')
    evidence_coverage = prov.get('evidence_coverage') or ('high' if raw_score and raw_score >= 80 else ('medium' if raw_score else 'none'))
    confidence = prov.get('confidence', 0.90 if raw_score is not None else 0.0)
    assumptions = prov.get('assumptions', [])
    missing_evidence = prov.get('missing_evidence', [] if raw_score is not None else [f"أدلة التحقق لـ {name}"])
    
    assessment_source = 'AI'
    actor = 'Qarar Specialist Council'
    timestamp = prov.get('timestamp') or datetime.now(timezone.utc).isoformat()
    review_history = list(prov.get('review_history') or [])
    override_history = list(prov.get('override_history') or [])
    original_score = prov.get('original_score', raw_score)
    original_assessment = prov.get('original_assessment', rationale)

    if override_entry:
        assessment_source = 'HUMAN'
        actor = override_entry.get('actor', 'Authorized Reviewer')
        timestamp = override_entry.get('timestamp', timestamp)
        override_history.append(override_entry)

    is_gate = bool(criterion.get('is_gate'))
    gate_passed = True
    gate_failure_reason = None
    
    if is_gate and raw_score is not None:
        if criterion.get('direction') == 'higher_better':
            threshold = criterion.get('gate_min') if criterion.get('gate_min') is not None else (criterion['scale_min'] + (criterion['scale_max'] - criterion['scale_min']) * 0.7)
            if raw_score < threshold:
                gate_passed = False
                gate_failure_reason = f"الدرجة {raw_score} أدنى من عتبة البوابة الإلزامية ({threshold})"
        else:
            threshold = criterion.get('gate_max') if criterion.get('gate_max') is not None else (criterion['scale_min'] + (criterion['scale_max'] - criterion['scale_min']) * 0.3)
            if raw_score > threshold:
                gate_passed = False
                gate_failure_reason = f"الدرجة {raw_score} تتجاوز السقف الإلزامي للبوابة ({threshold})"
    elif is_gate and raw_score is None:
        gate_passed = False
        gate_failure_reason = "لم يتم تقديم درجة للمعيار الإلزامي"

    return {
        'criterion_key': key,
        'criterion_name': name,
        'raw_score': raw_score,
        'normalized_score': normalized_score,
        'weighted_contribution': weighted_contrib,
        'weight': criterion['weight'],
        'weight_percentage': round(criterion['weight'] * 100, 2),
        'direction': criterion['direction'],
        'scale_min': criterion['scale_min'],
        'scale_max': criterion['scale_max'],
        'rationale': rationale,
        'evidence_references': evidence_refs,
        'source_ids': source_ids,
        'trust_level': trust_level,
        'evidence_coverage': evidence_coverage,
        'confidence': confidence,
        'assumptions': assumptions,
        'missing_evidence': missing_evidence,
        'assessment_method': 'deterministic-provenance-v9',
        'assessment_source': assessment_source,
        'original_assessment': original_assessment,
        'original_score': original_score,
        'review_history': review_history,
        'override_history': override_history,
        'actor': actor,
        'timestamp': timestamp,
        'is_gate': is_gate,
        'gate_passed': gate_passed,
        'gate_failure_reason': gate_failure_reason,
    }

def score_options(
    options: list[dict[str, Any]],
    weights: dict[str, Any] | None = None,
    criteria: list[dict[str, Any]] | None = None,
    tie_threshold: float = 0.01,
    overrides: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    configured = normalize_criteria(criteria, weights)
    output: list[dict[str, Any]] = []

    # Map overrides by option_id + criterion_key
    override_map: dict[str, dict[str, Any]] = {}
    for o in overrides or []:
        key = f"{o.get('option_id')}:{o.get('criterion_key')}"
        override_map[key] = o

    for option in options:
        opt_id = str(option.get('id', ''))
        raw_scores = option.get('criterion_scores') if isinstance(option, dict) else {}
        raw_scores = dict(raw_scores) if isinstance(raw_scores, dict) else {}
        opt_provenance = option.get('criterion_provenance') if isinstance(option, dict) else {}
        opt_provenance = dict(opt_provenance) if isinstance(opt_provenance, dict) else {}

        # Apply any override directly to raw score
        for criterion in configured:
            ov_key = f"{opt_id}:{criterion['key']}"
            if ov_key in override_map:
                raw_scores[criterion['key']] = override_map[ov_key]['new_score']

        details: list[dict[str, Any]] = []
        provenance_dict: dict[str, Any] = {}
        missing_required: list[str] = []
        gate_failures: list[dict[str, Any]] = []
        numerator = denominator = 0.0

        for criterion in configured:
            ckey = criterion['key']
            raw_val = raw_scores.get(ckey)
            norm_val = _normalized_score(raw_val, criterion)
            weighted_contrib = round(norm_val * criterion['weight'], 4) if norm_val is not None else None

            if norm_val is None:
                if criterion.get('missing_policy') == 'incomplete':
                    missing_required.append(ckey)
            else:
                numerator += norm_val * criterion['weight']
                denominator += criterion['weight']

            ov_entry = override_map.get(f"{opt_id}:{ckey}")
            cell_provenance = _build_provenance_entry(
                option, criterion, raw_val, norm_val, weighted_contrib, opt_provenance, ov_entry
            )
            provenance_dict[ckey] = cell_provenance

            if cell_provenance.get('is_gate') and not cell_provenance.get('gate_passed'):
                gate_failures.append({
                    'criterion_key': ckey,
                    'criterion_name': criterion['name'],
                    'raw_score': raw_val,
                    'reason': cell_provenance.get('gate_failure_reason'),
                })

            details.append({
                **criterion,
                'raw_score': raw_val,
                'normalized_score': norm_val,
                'weighted_contribution': weighted_contrib,
                'provenance': cell_provenance,
                'gate_passed': cell_provenance.get('gate_passed', True),
                'gate_failure_reason': cell_provenance.get('gate_failure_reason'),
            })

        score_valid = (not missing_required) and (denominator > 0)
        weighted_score = round(numerator / denominator, 2) if score_valid else None
        is_disqualified = len(gate_failures) > 0
        disqualification_reason = (
            f"لم يجتز البوابة الإلزامية: {gate_failures[0]['criterion_name']} ({gate_failures[0]['reason']})"
            if is_disqualified else None
        )

        item = {
            **option,
            'criterion_scores': raw_scores,
            'criterion_details': details,
            'criterion_provenance': provenance_dict,
            'score_completeness': round(sum(x['normalized_score'] is not None for x in details) / len(details), 4),
            'missing_criteria': missing_required,
            'score_valid': score_valid,
            'weighted_score': weighted_score,
            'is_disqualified': is_disqualified,
            'disqualification_reason': disqualification_reason,
            'gate_failures': gate_failures,
            'status': 'disqualified' if is_disqualified else ('valid' if score_valid else 'incomplete'),
            'calculation_metadata': {
                'method': 'weighted-normalized-v9-provenance',
                'normalized_weight_total': round(denominator, 6),
                'missing_policy': 'explicit',
                'tie_threshold': tie_threshold,
                'gates_evaluated': sum(bool(c.get('is_gate')) for c in configured),
                'gates_passed': len(gate_failures) == 0,
            },
        }
        output.append(item)

    # Qualified valid options ranked first by weighted_score desc; disqualified or invalid options ranked below
    def rank_sort_key(x: dict[str, Any]) -> tuple:
        is_qual = 1 if (x['score_valid'] and not x.get('is_disqualified')) else 0
        score_val = x['weighted_score'] if x['weighted_score'] is not None else -999.0
        return (is_qual, score_val)

    output.sort(key=rank_sort_key, reverse=True)

    # Lead and rank status for top qualified option
    qualified = [x for x in output if x['score_valid'] and not x.get('is_disqualified')]
    if len(qualified) > 1:
        diff = round(qualified[0]['weighted_score'] - qualified[1]['weighted_score'], 2)
        qualified[0]['rank_status'] = 'tied' if diff <= tie_threshold else 'leader'
        qualified[0]['lead_over_next'] = diff
    elif len(qualified) == 1:
        qualified[0]['rank_status'] = 'leader'
        qualified[0]['lead_over_next'] = qualified[0]['weighted_score']

    for index, item in enumerate(output, 1):
        item['rank'] = index

    return output

def evaluate_business_scenarios(
    options: list[dict[str, Any]],
    criteria: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    configured = normalize_criteria(criteria)
    baseline = score_options(options, criteria=configured)
    baseline_leader = (
        baseline[0].get('id')
        if baseline and baseline[0].get('score_valid') and not baseline[0].get('is_disqualified')
        else None
    )

    scenario_results: list[dict[str, Any]] = []

    for preset in SCENARIO_PRESETS:
        preset_id = preset['id']
        strategy = preset.get('strategy')
        
        changed_criteria: list[dict[str, Any]] = []
        weight_map: dict[str, float] = {}

        if strategy == 'equal':
            equal_weight = 1.0 / len(configured)
            for c in configured:
                c_copy = dict(c)
                c_copy['weight'] = equal_weight
                changed_criteria.append(c_copy)
                weight_map[c['key']] = round(equal_weight, 4)
        elif strategy == 'boost_keys':
            boost_keys = set(preset.get('boost_keys', []))
            factor = preset.get('boost_factor', 2.0)
            raw_weights: dict[str, float] = {}
            for c in configured:
                is_boost = c['key'] in boost_keys or any(bk in c['key'] for bk in boost_keys)
                raw_weights[c['key']] = c['weight'] * (factor if is_boost else 1.0)
            total_raw = sum(raw_weights.values()) or 1.0
            for c in configured:
                c_copy = dict(c)
                norm_w = raw_weights[c['key']] / total_raw
                c_copy['weight'] = norm_w
                changed_criteria.append(c_copy)
                weight_map[c['key']] = round(norm_w, 4)
        else:
            changed_criteria = [dict(c) for c in configured]
            weight_map = {c['key']: c['weight'] for c in configured}

        scenario_scored = score_options(options, criteria=changed_criteria)
        scenario_leader = (
            scenario_scored[0].get('id')
            if scenario_scored and scenario_scored[0].get('score_valid') and not scenario_scored[0].get('is_disqualified')
            else None
        )
        leader_changed = (baseline_leader != scenario_leader)
        margin = scenario_scored[0].get('lead_over_next', 0) if scenario_scored else 0
        stability = 'highly_sensitive' if leader_changed or margin < 2 else ('moderately_sensitive' if margin < 8 else 'stable')

        explanation_ar = (
            f"تغير المتصدر من '{baseline_leader}' إلى '{scenario_leader}' بسبب ارتفاع أوزان المعايير المرجحة في سيناريو {preset['title_ar']}."
            if leader_changed
            else f"المتصدر '{baseline_leader}' حافظ على تقدمه بفارق {margin} نقطة تحت سيناريو {preset['title_ar']}."
        )
        explanation_en = (
            f"The leader changed from '{baseline_leader}' to '{scenario_leader}' due to increased weight on prioritized criteria in the {preset['title_en']} scenario."
            if leader_changed
            else f"The baseline leader '{baseline_leader}' maintained its lead by a margin of {margin} points under the {preset['title_en']} scenario."
        )

        scenario_results.append({
            'preset_id': preset_id,
            'title_ar': preset['title_ar'],
            'title_en': preset['title_en'],
            'description_ar': preset['description_ar'],
            'description_en': preset['description_en'],
            'weights': weight_map,
            'baseline_leader': baseline_leader,
            'scenario_leader': scenario_leader,
            'leader_changed': leader_changed,
            'stability': stability,
            'margin': margin,
            'explanation_ar': explanation_ar,
            'explanation_en': explanation_en,
            'baseline_ranking': [{'id': x.get('id'), 'rank': x.get('rank'), 'score': x.get('weighted_score'), 'status': x.get('status')} for x in baseline],
            'scenario_ranking': [{'id': x.get('id'), 'rank': x.get('rank'), 'score': x.get('weighted_score'), 'status': x.get('status')} for x in scenario_scored],
        })

    return scenario_results

def sensitivity_analysis(
    options: list[dict[str, Any]],
    criteria: list[dict[str, Any]],
    weight_changes: dict[str, float] | None = None,
    score_changes: dict[str, dict[str, float]] | None = None,
) -> dict[str, Any]:
    configured = normalize_criteria(criteria)
    baseline = score_options(options, criteria=configured)
    changed = []
    for criterion in configured:
        new = dict(criterion)
        if weight_changes and criterion['key'] in weight_changes:
            new['weight'] = weight_changes[criterion['key']]
        changed.append(new)
    adjusted = []
    for option in options:
        copy = {**option, 'criterion_scores': dict(option.get('criterion_scores') or {})}
        for key, value in (score_changes or {}).get(str(option.get('id')), {}).items():
            copy['criterion_scores'][key] = value
        adjusted.append(copy)
    scenario = score_options(adjusted, criteria=changed)
    before = baseline[0].get('id') if baseline and baseline[0].get('score_valid') and not baseline[0].get('is_disqualified') else None
    after = scenario[0].get('id') if scenario and scenario[0].get('score_valid') and not scenario[0].get('is_disqualified') else None
    margin = (scenario[0].get('lead_over_next') or 0) if scenario else 0
    stability = 'highly_sensitive' if before != after or margin < 2 else ('moderately_sensitive' if margin < 8 else 'stable')
    
    # Also evaluate all standard business scenario presets
    presets_evaluation = evaluate_business_scenarios(options, criteria)

    return {
        'baseline': baseline,
        'scenario': scenario,
        'baseline_leader': before,
        'scenario_leader': after,
        'stability': stability,
        'changed_recommendation': before != after,
        'margin': margin,
        'presets': presets_evaluation,
        'note': 'Sensitivity is directional, not a probability forecast.',
    }

def compose_confidence(
    evidence: dict[str, Any],
    scored_options: list[dict[str, Any]],
    *,
    clarifications: list[str] | None = None,
    assumptions: list[str] | None = None,
    conflicts: list[str] | None = None,
    sensitivity: dict[str, Any] | None = None,
) -> tuple[float, dict[str, Any]]:
    facts = evidence.get('facts') or []
    unknowns = evidence.get('missing_information') or []
    sources = evidence.get('sources') or []
    context = len(facts) / (len(facts) + len(unknowns)) if facts or unknowns else 0
    coverage = min(1.0, len(sources) / 3)
    trust = {'A': 1.0, 'B': 0.8, 'C': 0.55, 'D': 0.25}
    quality = sum(trust.get(str(x.get('trust_level', 'C')).upper(), 0.4) for x in sources) / len(sources) if sources else 0
    completeness = sum(float(x.get('score_completeness', 0)) for x in scored_options) / len(scored_options) if scored_options else 0
    valid = sorted([float(x['weighted_score']) for x in scored_options if x.get('score_valid') and not x.get('is_disqualified')], reverse=True)
    differentiation = min(1.0, (valid[0] - valid[1]) / 20.0) if len(valid) > 1 else (0.5 if len(valid) == 1 else 0.0)
    clarification_factor = max(0.0, 1.0 - min(1.0, len(clarifications or unknowns) / 5.0))
    assumption_factor = max(0.0, 1.0 - min(1.0, len(assumptions or []) / 5.0))
    conflict_factor = max(0.0, 1.0 - min(1.0, len(conflicts or []) / 3.0))
    stability = {'stable': 1.0, 'moderately_sensitive': 0.6, 'highly_sensitive': 0.2}.get((sensitivity or {}).get('stability'), 0.5)
    factors = {
        'context_completeness': context,
        'evidence_coverage': coverage,
        'source_quality': quality,
        'scoring_completeness': completeness,
        'option_differentiation': differentiation,
        'clarification_resolution': clarification_factor,
        'assumption_control': assumption_factor,
        'conflict_control': conflict_factor,
        'sensitivity_stability': stability,
    }
    weights = {
        'context_completeness': 0.15,
        'evidence_coverage': 0.12,
        'source_quality': 0.12,
        'scoring_completeness': 0.18,
        'option_differentiation': 0.10,
        'clarification_resolution': 0.10,
        'assumption_control': 0.08,
        'conflict_control': 0.07,
        'sensitivity_stability': 0.08,
    }
    value = round(sum(factors[k] * weights[k] for k in weights), 2)
    positives = [k for k, v in factors.items() if v >= 0.75]
    uncertainties = [k for k, v in factors.items() if v < 0.5]
    return value, {
        'method': 'deterministic-v2',
        'formula_weights': weights,
        'factors': {k: round(v, 4) for k, v in factors.items()},
        'positive_factors': positives,
        'uncertainty_factors': uncertainties,
        'improvement_actions': [f'Improve {x.replace("_", " ")}' for x in uncertainties],
        'uncalibrated_model_confidence_excluded': True,
    }
