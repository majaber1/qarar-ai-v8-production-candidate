from __future__ import annotations
from app.core.config import settings

OFFICIAL_SOURCE_HINTS = {
    'nca.gov.sa': 'Saudi National Cybersecurity Authority (NCA)',
    'dga.gov.sa': 'Saudi Digital Government Authority (DGA)',
    'sdaia.gov.sa': 'Saudi Data & AI Authority / PDPL ecosystem',
    'cst.gov.sa': 'Communications, Space & Technology Commission (CST)',
}

def research_status():
    return {'enabled': settings.research_enabled, 'public_web': settings.public_web_enabled,
            'official_domains': settings.official_domain_list,
            'modes': ['organization_only', 'official_plus_organization', 'full_research']}

def web_research(query: str, mode: str = 'official_plus_organization'):
    if not (settings.research_enabled and settings.public_web_enabled and settings.ai_enabled and settings.ai_api_key):
        return {'status': 'disabled', 'query': query, 'mode': mode, 'results': [], 'official_domains': settings.official_domain_list}
    try:
        from openai import OpenAI
        c = OpenAI(api_key=settings.ai_api_key, timeout=settings.ai_timeout_seconds)
        domains = settings.official_domain_list if mode == 'official_plus_organization' else []
        scoped = query + ("\nPrefer authoritative official sources from: " + ', '.join(domains) if domains else '')
        r = c.responses.create(model=settings.ai_model, tools=[{'type': 'web_search'}], input=scoped)
        sources = []
        for out in getattr(r, 'output', []) or []:
            for part in getattr(out, 'content', []) or []:
                for ann in getattr(part, 'annotations', []) or []:
                    url, title = getattr(ann, 'url', None), getattr(ann, 'title', None)
                    if url and url not in [x['url'] for x in sources]:
                        sources.append({'url': url, 'title': title or url,
                                        'trust_level': 'A' if any(d in url for d in domains) else 'C'})
        return {'status': 'ok', 'query': query, 'mode': mode, 'answer': getattr(r, 'output_text', ''), 'results': sources}
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'results': []}
