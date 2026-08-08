from __future__ import annotations
import json
import logging
import sys
from datetime import datetime, timezone

_logger = logging.getLogger('qarar')


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            'ts': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'event': record.getMessage(),
        }
        extra = getattr(record, 'qarar_fields', None)
        if extra:
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging():
    if _logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)
    _logger.propagate = False


def log_event(event: str, **fields):
    """Structured JSON log line. Correlate across services with request_id/tenant_id fields.
    Fields carried here map onto OpenTelemetry span attributes if OTEL exporters are wired in later —
    the field names (request_id, tenant_id, agent, duration_ms) are chosen to match that convention."""
    _logger.info(event, extra={'qarar_fields': fields})
