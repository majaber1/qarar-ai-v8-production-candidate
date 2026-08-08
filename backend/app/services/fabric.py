from __future__ import annotations
import json, math, re
from sqlalchemy import select, delete, text
from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.models.fabric import KnowledgeSource, KnowledgeChunk
from app.models.platform import ScanResult
from app.services.knowledge import extract_text
from app.services.malware_scan import scan_bytes
from app.services.object_storage import storage
from app.services.security_text import flag_suspicious

TRUST = {'A': 1.0, 'B': .78, 'C': .55, 'D': .30}

def chunk_text(text: str, size: int | None = None, overlap: int | None = None):
    size = size or settings.chunk_chars
    overlap = overlap or settings.chunk_overlap
    text = '\n'.join(x.strip() for x in text.splitlines() if x.strip())
    if not text:
        return []
    out, start = [], 0
    while start < len(text):
        end = min(len(text), start + size)
        piece = text[start:end]
        if end < len(text):
            cut = max(piece.rfind('\n'), piece.rfind('. '), piece.rfind('؟ '))
            if cut > size * .55:
                end = start + cut + 1
                piece = text[start:end]
        out.append(piece.strip())
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return [x for x in out if x]

def embed(texts: list[str]) -> list[list[float] | None]:
    if not (settings.ai_enabled and settings.ai_api_key):
        return [None] * len(texts)
    try:
        from openai import OpenAI
        c = OpenAI(api_key=settings.ai_api_key, timeout=settings.ai_timeout_seconds)
        r = c.embeddings.create(model=settings.embedding_model, input=texts)
        return [x.embedding for x in r.data]
    except Exception:
        return [None] * len(texts)


# --- pgvector storage (Postgres only). SQLite dev mode keeps embeddings inline as JSON on the
# chunk row and falls back to a Python-side scan — acceptable for a local dev corpus, not for an
# enterprise archive. This is the reason V6 defaults the pilot stack to Postgres. ---

_pgvector_ready = False

def _ensure_pgvector():
    global _pgvector_ready
    if _pgvector_ready or not settings.is_postgres:
        return
    with engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
        conn.execute(text(
            f'CREATE TABLE IF NOT EXISTS knowledge_chunk_vectors_v6 ('
            f'chunk_id INTEGER PRIMARY KEY, tenant_id TEXT NOT NULL, case_id INTEGER, '
            f'embedding vector({settings.embedding_dimensions}))'
        ))
        conn.execute(text(
            'CREATE INDEX IF NOT EXISTS knowledge_chunk_vectors_v6_ivfflat '
            'ON knowledge_chunk_vectors_v6 USING ivfflat (embedding vector_cosine_ops)'
        ))
        conn.execute(text(
            'CREATE INDEX IF NOT EXISTS knowledge_chunk_vectors_v6_tenant ON knowledge_chunk_vectors_v6 (tenant_id)'
        ))
    _pgvector_ready = True


def _upsert_vector(chunk_id: int, tenant_id: str, case_id: int | None, vector: list[float]):
    _ensure_pgvector()
    literal = '[' + ','.join(f'{v:.8f}' for v in vector) + ']'
    with engine.begin() as conn:
        conn.execute(text(
            'INSERT INTO knowledge_chunk_vectors_v6 (chunk_id, tenant_id, case_id, embedding) '
            'VALUES (:chunk_id, :tenant_id, :case_id, CAST(:embedding AS vector)) '
            'ON CONFLICT (chunk_id) DO UPDATE SET embedding = EXCLUDED.embedding, tenant_id = EXCLUDED.tenant_id, case_id = EXCLUDED.case_id'
        ), {'chunk_id': chunk_id, 'tenant_id': tenant_id, 'case_id': case_id, 'embedding': literal})


def ingest_source(source_id: int):
    db = SessionLocal()
    s = None
    try:
        s = db.get(KnowledgeSource, source_id)
        if not s:
            return
        s.status = 'processing'
        db.commit()
        raw = storage().get(s.object_key) if s.object_key else b''

        scan_status, engine_name, detail = scan_bytes(raw)
        db.add(ScanResult(tenant_id=s.tenant_id, source_id=s.id, status=scan_status, engine=engine_name, detail=detail))
        db.commit()
        if scan_status == 'infected':
            s.status = 'quarantined'
            s.error = f'Malware scan flagged this file ({detail or "signature match"}) — not indexed.'
            db.commit()
            return

        text_content = extract_text(s.title, raw)
        suspicious = flag_suspicious(text_content)
        chunks = chunk_text(text_content)
        vectors = embed(chunks)
        db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.source_id == s.id))
        new_chunks = []
        for i, (content, vec) in enumerate(zip(chunks, vectors)):
            ch = KnowledgeChunk(
                source_id=s.id, tenant_id=s.tenant_id, case_id=s.case_id,
                chunk_index=i, content=content,
                embedding_json=json.dumps(vec) if vec else None,
                metadata_json=json.dumps({
                    'title': s.title, 'source_type': s.source_type, 'trust_level': s.trust_level,
                    'suspicious_patterns': suspicious,
                }),
            )
            db.add(ch)
            new_chunks.append((ch, vec))
        db.commit()
        if settings.is_postgres:
            for ch, vec in new_chunks:
                if vec:
                    _upsert_vector(ch.id, s.tenant_id, s.case_id, vec)
        s.status = 'ready'
        s.error = None
        if suspicious:
            s.error = None  # not a failure, but flagged for Developer/Admin review via metadata
        db.commit()
    except Exception as e:
        if s:
            s.status = 'failed'
            s.error = str(e)
            db.commit()
    finally:
        db.close()

def _terms(s: str):
    return set(re.findall(r'[A-Za-z0-9_؀-ۿ]{2,}', s.lower()))

def lexical(q, c):
    qt, ct = _terms(q), _terms(c)
    return 0 if not qt else len(qt & ct) / max(1, len(qt))

def cosine(a, b):
    if not a or not b:
        return 0
    d = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return d / (na * nb) if na and nb else 0


def _score_rows(question: str, rows) -> list[dict]:
    scored = []
    for ch, s in rows:
        lex = lexical(question, ch.content)
        trust = TRUST.get(s.trust_level, .5)
        # Vector similarity is folded in by the caller for the Postgres path (see _hybrid_search_pg);
        # for the SQLite fallback we compute cosine here against the inline JSON embedding.
        cv = json.loads(ch.embedding_json) if ch.embedding_json else None
        scored.append({'chunk': ch, 'source': s, 'lexical': lex, 'trust': trust, 'embedding': cv})
    return scored


def _finalize(question: str, qv, scored: list[dict], limit: int) -> list[dict]:
    out = []
    for item in scored:
        vec = max(0, cosine(qv, item['embedding'])) if qv else 0
        score = settings.hybrid_vector_weight * vec + settings.hybrid_lexical_weight * item['lexical'] + settings.hybrid_trust_weight * item['trust']
        ch, s = item['chunk'], item['source']
        out.append({'chunk_id': ch.id, 'source_id': s.id, 'title': s.title, 'source_type': s.source_type,
                     'source_ref': s.source_ref, 'trust_level': s.trust_level, 'text': ch.content, 'score': round(score, 4)})
    out.sort(key=lambda x: x['score'], reverse=True)
    return out[:limit]


def _hybrid_search_scan(question: str, case_id: int | None, tenant_id: str, limit: int, allowed_types: list[str] | None):
    """SQLite / dev-mode fallback: scans every ready chunk for the tenant. Fine for a demo corpus,
    not for an enterprise archive — use POSTGRES for the pgvector-backed path."""
    db = SessionLocal()
    try:
        stmt = select(KnowledgeChunk, KnowledgeSource).join(KnowledgeSource, KnowledgeSource.id == KnowledgeChunk.source_id).where(
            KnowledgeChunk.tenant_id == tenant_id, KnowledgeSource.status == 'ready')
        if case_id is not None:
            stmt = stmt.where((KnowledgeChunk.case_id == case_id) | (KnowledgeChunk.case_id.is_(None)))
        if allowed_types:
            stmt = stmt.where(KnowledgeSource.source_type.in_(allowed_types))
        rows = db.execute(stmt).all()
        qv = embed([question])[0]
        scored = _score_rows(question, rows)
        return _finalize(question, qv, scored, limit)
    finally:
        db.close()


def _hybrid_search_pg(question: str, case_id: int | None, tenant_id: str, limit: int, allowed_types: list[str] | None):
    """Postgres path: bound the candidate set with an indexed pgvector ANN query plus a native
    full-text search query, instead of scanning every chunk in the tenant."""
    _ensure_pgvector()
    candidate_k = max(50, limit * 5)
    qv = embed([question])[0]
    candidate_ids: set[int] = set()

    with engine.connect() as conn:
        if qv:
            literal = '[' + ','.join(f'{v:.8f}' for v in qv) + ']'
            case_clause = 'AND (case_id = :case_id OR case_id IS NULL)' if case_id is not None else ''
            rows = conn.execute(text(
                f'SELECT chunk_id FROM knowledge_chunk_vectors_v6 WHERE tenant_id = :tenant_id {case_clause} '
                f'ORDER BY embedding <=> CAST(:qv AS vector) LIMIT :k'
            ), {'tenant_id': tenant_id, 'case_id': case_id, 'qv': literal, 'k': candidate_k}).all()
            candidate_ids.update(r[0] for r in rows)

        # OR-joined tsquery (not plainto_tsquery, which ANDs every term with no stemming and would
        # miss a chunk on a single word-form mismatch like "migration" vs "migrations"). This mirrors
        # the recall-oriented "any term overlap counts" behavior of the original Python lexical scorer.
        terms = sorted(_terms(question))
        if terms:
            tsquery = ' | '.join(t.replace("'", "") for t in terms)
            lex_rows = conn.execute(text(
                "SELECT c.id FROM knowledge_chunks_v5 c JOIN knowledge_sources_v5 s ON s.id = c.source_id "
                "WHERE c.tenant_id = :tenant_id AND s.status = 'ready' "
                "AND to_tsvector('simple', c.content) @@ to_tsquery('simple', :q) "
                "LIMIT :k"
            ), {'tenant_id': tenant_id, 'q': tsquery, 'k': candidate_k}).all()
            candidate_ids.update(r[0] for r in lex_rows)

    if not candidate_ids:
        return []

    db = SessionLocal()
    try:
        stmt = select(KnowledgeChunk, KnowledgeSource).join(KnowledgeSource, KnowledgeSource.id == KnowledgeChunk.source_id).where(
            KnowledgeChunk.id.in_(candidate_ids), KnowledgeSource.status == 'ready')
        if allowed_types:
            stmt = stmt.where(KnowledgeSource.source_type.in_(allowed_types))
        rows = db.execute(stmt).all()
        scored = _score_rows(question, rows)
        return _finalize(question, qv, scored, limit)
    finally:
        db.close()


def hybrid_search(question: str, case_id: int | None = None, tenant_id: str | None = None, limit: int = 10, allowed_types: list[str] | None = None):
    if not tenant_id:
        raise ValueError('tenant_id is required for knowledge retrieval')
    if settings.is_postgres:
        return _hybrid_search_pg(question, case_id, tenant_id, limit, allowed_types)
    return _hybrid_search_scan(question, case_id, tenant_id, limit, allowed_types)
