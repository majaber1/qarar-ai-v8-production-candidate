from dataclasses import dataclass, field
from app.services.contracts import CaseInput
ALWAYS=['evidence','risk']
KEYWORDS={
'policy':['policy','governance','approval','سياسة','حوكمة','موافقة'],'legal':['legal','law','contract','jurisdiction','قانون','عقد','تشريع'],'financial':['budget','cost','roi','tco','ميزانية','تكلفة','مالي'],'strategy':['strategy','objective','vision','استراتيجية','هدف','رؤية'],'stakeholder':['stakeholder','owner','approver','team','مالك','موافق','فريق'],'timeline':['deadline','delay','milestone','schedule','موعد','تأخير','جدول'],'cybersecurity':['security','cyber','iam','أمن','سيبراني'],'architecture':['architecture','integration','togaf','معمارية','تكامل'],'cloud':['aws','azure','gcp','oci','nutanix','cloud','region','سحابة'],'procurement':['rfp','sow','sla','vendor','procurement','مورد','مشتريات'],'project_management':['project','blocker','status','pmo','مشروع','معوق','حالة'],'data_governance':['data','classification','residency','retention','privacy','بيانات','تصنيف','إقامة','خصوصية'],'compliance':['compliance','nca','dga','pdpl','iso','cobit','امتثال','التزام'],'business_continuity':['dr','bcp','rto','rpo','disaster','continuity','تعافي','استمرارية'],'operations':['operations','support','monitoring','runbook','تشغيل','دعم','مراقبة'],'hr':['hr','training','skills','employee','موارد بشرية','تدريب','مهارات']}

@dataclass
class Plan:
    selected: list[str]
    skipped: list[str]
    stages: list[list[str]]
    skip_reasons: dict[str, str] = field(default_factory=dict)


def build_plan(case: CaseInput, all_specialists: list[str]) -> Plan:
    text = f'{case.title} {case.description} {case.category or ""}'.lower()
    selected = list(ALWAYS)
    matched_words: dict[str, str] = {}
    for n, words in KEYWORDS.items():
        hit = next((w for w in words if w.lower() in text), None)
        if hit:
            selected.append(n)
            matched_words[n] = hit
    selected = list(dict.fromkeys(selected))
    parallel = [x for x in selected if x != 'evidence']
    stages = [['evidence']] + ([parallel] if parallel else []) + [['options'], ['critic'], ['chief_advisor']]
    skipped = [x for x in all_specialists if x not in selected]
    skip_reasons = {
        n: f"لم يتم رصد كلمات مرتبطة بمجال {n} في وصف القضية (مثال: {', '.join(KEYWORDS.get(n, [])[:3])})"
        for n in skipped if n in KEYWORDS
    }
    return Plan(selected, skipped, stages, skip_reasons)
