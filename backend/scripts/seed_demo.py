"""Seed 4 demo cases with sample evidence for pilot demonstrations."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal, engine, Base
from app.models.case import DecisionCase
from app.models.fabric import KnowledgeSource, KnowledgeChunk
from app.models.platform import AuditEvent
from app.services.object_storage import storage as get_storage
from datetime import datetime, timezone

TENANT = 'demo'
ACTOR = 'seed-script'

CASES = [
    {
        'title': 'ترحيل البيانات إلى السحابة — AWS أم Azure؟',
        'description': 'الوزارة تدرس ترحيل أنظمة البريد والملفات إلى السحابة. الخيارات المطروحة هي AWS وAzure وسيناريو البقاء محليًا. يجب مراعاة أمن البيانات والتكلفة والامتثال التنظيمي.',
        'urgency': 'high',
        'category': 'technology',
        'language': 'ar',
    },
    {
        'title': 'تجديد عقد البرمجيات المؤسسية — Oracle vs open-source',
        'description': 'العقد الحالي مع Oracle ينتهي خلال 90 يومًا. فريق التقنية يقترح الانتقال إلى PostgreSQL مفتوح المصدر. يجب تقييم تكلفة الترحيل، المخاطر التشغيلية، والدعم الفني.',
        'urgency': 'critical',
        'category': 'finance',
        'language': 'ar',
    },
    {
        'title': 'Cybersecurity framework adoption — NIST vs ISO 27001',
        'description': 'The organization needs to adopt a formal cybersecurity framework. Two options are under consideration: NIST CSF and ISO 27001. Budget, timeline, and compliance requirements with NCA regulations must be factored in.',
        'urgency': 'medium',
        'category': 'technology',
        'language': 'en',
    },
    {
        'title': 'إنشاء مركز ابتكار داخلي أم التعاقد مع شريك خارجي',
        'description': 'الإدارة العليا تريد تسريع الابتكار الرقمي. هل الأفضل بناء مركز ابتكار داخلي بتكلفة أعلى وتحكم كامل، أم التعاقد مع شريك خارجي بتكلفة أقل ومرونة أكبر؟',
        'urgency': 'medium',
        'category': 'strategy',
        'language': 'ar',
    },
]

EVIDENCE = [
    ('تقرير هيئة الاتصالات — التنظيم السحابي', 'A', 'بحسب التعميم رقم 2024/15 الصادر عن هيئة الاتصالات وتقنية المعلومات، يُسمح بتخزين البيانات الحكومية في مراكز بيانات سحابية مرخصة داخل المملكة.'),
    ('تحليل تكلفة الترحيل — إدارة التقنية', 'B', 'التكلفة المتوقعة لترحيل البريد والملفات إلى Azure: 1.2 مليون ريال. AWS: 1.4 مليون ريال. البقاء محليًا: 800 ألف ريال سنويًا للصيانة.'),
    ('Oracle renewal quote 2026', 'B', 'Oracle database enterprise license renewal: $450,000/year for 3-year term. Includes 24/7 support and quarterly patches.'),
    ('NCA Essential Cybersecurity Controls', 'A', 'The National Cybersecurity Authority requires all government entities to implement ECC-1:2018 controls. Both NIST CSF and ISO 27001 map to these requirements with varying degrees of coverage.'),
]


def seed():
    Base.metadata.create_all(bind=engine)
    store = get_storage()

    with SessionLocal() as db:
        existing = db.query(DecisionCase).filter_by(tenant_id=TENANT).count()
        if existing:
            print(f'Demo tenant already has {existing} cases — skipping seed.')
            return

        case_ids = []
        for c in CASES:
            obj = DecisionCase(tenant_id=TENANT, created_by=ACTOR, **c)
            db.add(obj)
            db.flush()
            case_ids.append(obj.id)
            db.add(AuditEvent(tenant_id=TENANT, actor=ACTOR, event_type='case_created',
                              resource_type='case', resource_id=str(obj.id),
                              metadata_json='{"source":"seed_demo"}'))

        for i, (title, trust, text) in enumerate(EVIDENCE):
            cid = case_ids[i % len(case_ids)]
            key = store.put(f'seed-{i}.txt', text.encode('utf-8'))
            src = KnowledgeSource(
                tenant_id=TENANT, case_id=cid, source_type='document',
                title=title, source_ref='seed', object_key=key,
                trust_level=trust, status='ready',
            )
            db.add(src)
            db.flush()
            db.add(KnowledgeChunk(
                source_id=src.id, tenant_id=TENANT, case_id=cid,
                chunk_index=0, content=text,
            ))

        db.commit()
        print(f'Seeded {len(CASES)} demo cases and {len(EVIDENCE)} evidence items for tenant "{TENANT}".')


if __name__ == '__main__':
    seed()
