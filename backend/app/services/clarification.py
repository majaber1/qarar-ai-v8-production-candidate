from __future__ import annotations
from app.services.fabric import hybrid_search

# Conservative heuristic: only treat an unknown as safely inferable if it explicitly describes
# something low-stakes/operational. Anything about approval authority, budget, legal or compliance
# always goes to a human — Qarar never silently assumes those.
_LOW_STAKES_HINTS = ['تفضيل', 'تنسيق', 'صياغة', 'ترتيب', 'preference', 'formatting', 'scheduling detail']
_RETRIEVAL_SCORE_THRESHOLD = 0.35
_MAX_QUESTIONS = 5


def classify_missing_information(missing: list[str], tenant_id: str, case_id: int | None) -> dict:
    auto_retrievable, inferable, human_required = [], [], []
    for item in missing:
        try:
            hits = hybrid_search(item, case_id=case_id, tenant_id=tenant_id, limit=1)
        except Exception:
            hits = []
        if hits and hits[0]['score'] >= _RETRIEVAL_SCORE_THRESHOLD:
            auto_retrievable.append({'item': item, 'source_id': hits[0]['source_id'], 'score': hits[0]['score']})
            continue
        if any(h in item for h in _LOW_STAKES_HINTS):
            inferable.append(item)
            continue
        human_required.append(item)

    return {
        'auto_retrievable': auto_retrievable,
        'inferable': inferable,
        'human_required': human_required,
        'top_questions': human_required[:_MAX_QUESTIONS],
    }
