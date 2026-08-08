import hashlib
import hmac
import time
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.security import AutomationCallbackReceipt

def verify_callback(run_id: int, body: bytes, timestamp: str | None, nonce: str | None, signature: str | None) -> None:
    if not settings.automation_callback_secret:
        raise PermissionError('Callback verification is not configured')
    if not timestamp or not nonce or not signature:
        raise PermissionError('Missing signed callback headers')
    try:
        ts = int(timestamp)
    except ValueError as exc:
        raise PermissionError('Invalid callback timestamp') from exc
    if abs(int(time.time()) - ts) > settings.automation_callback_max_skew_seconds:
        raise PermissionError('Expired callback timestamp')
    message = timestamp.encode() + b'.' + nonce.encode() + b'.' + body
    expected = hmac.new(settings.automation_callback_secret.encode(), message, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature.removeprefix('sha256=')):
        raise PermissionError('Invalid callback signature')
    try:
        with SessionLocal() as db:
            db.add(AutomationCallbackReceipt(run_id=run_id, nonce=nonce))
            db.commit()
    except IntegrityError as exc:
        raise PermissionError('Callback replay detected') from exc
