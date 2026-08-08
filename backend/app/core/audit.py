from __future__ import annotations
import json
import logging
from app.core.database import SessionLocal
from app.models.platform import AuditEvent
log=logging.getLogger(__name__)


def record_audit(tenant_id: str, actor: str, event_type: str, *, auth_type: str = 'api_key',
                  resource_type: str | None = None, resource_id: str | None = None,
                  request_id: str | None = None, metadata: dict | None = None) -> None:
    """Append an immutable audit row. Never raises — an audit failure must not break the request."""
    try:
        with SessionLocal() as db:
            db.add(AuditEvent(
                tenant_id=tenant_id, actor=actor, auth_type=auth_type, event_type=event_type,
                resource_type=resource_type, resource_id=str(resource_id) if resource_id is not None else None,
                request_id=request_id,
                metadata_json=json.dumps(metadata, ensure_ascii=False, default=str) if metadata else None,
            ))
            db.commit()
    except Exception:
        log.exception('Failed to persist audit event tenant=%s actor=%s event=%s',tenant_id,actor,event_type)
