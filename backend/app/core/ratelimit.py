from __future__ import annotations
import time
import logging
from collections import defaultdict, deque
from datetime import datetime, timezone
from threading import Lock
from sqlalchemy import select, func
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.platform import CostBudget, UsageRecord
log=logging.getLogger(__name__)


class SlidingWindowLimiter:
    """In-process sliding-window limiter. Sufficient for a single-process pilot deployment;
    replace the store with Redis before running multiple API replicas."""

    def __init__(self):
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, limit: int, window_seconds: float = 60.0) -> bool:
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > window_seconds:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            if len(self._hits)>10000:
                stale=[k for k,v in self._hits.items() if not v or now-v[-1]>window_seconds]
                for old in stale[:1000]:self._hits.pop(old,None)
            return True


limiter = SlidingWindowLimiter()


def check_rate_limit(user_key: str, tenant_key: str) -> tuple[bool, str]:
    if not settings.rate_limit_enabled:
        return True, ''
    if not limiter.allow(f'user:{user_key}', settings.rate_limit_requests_per_minute_user):
        return False, 'Per-user rate limit exceeded'
    if not limiter.allow(f'tenant:{tenant_key}', settings.rate_limit_requests_per_minute_tenant):
        return False, 'Per-tenant rate limit exceeded'
    return True, ''


def check_ai_rate_limit(user_key: str) -> tuple[bool, str]:
    if not settings.rate_limit_enabled:
        return True, ''
    if not limiter.allow(f'ai:{user_key}', settings.rate_limit_ai_requests_per_minute_user):
        return False, 'Per-user AI request rate limit exceeded'
    return True, ''


def _budget_for(tenant_id: str) -> CostBudget:
    with SessionLocal() as db:
        b = db.scalar(select(CostBudget).where(CostBudget.tenant_id == tenant_id))
        if b:
            return b
        return CostBudget(tenant_id=tenant_id, daily_budget_usd=settings.default_tenant_daily_budget_usd,
                           case_run_budget_usd=settings.default_case_run_budget_usd)


def spent_today_usd(tenant_id: str) -> float:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    with SessionLocal() as db:
        total = db.scalar(
            select(func.coalesce(func.sum(UsageRecord.cost_usd), 0.0)).where(
                UsageRecord.tenant_id == tenant_id, UsageRecord.created_at >= start
            )
        )
        return float(total or 0.0)


def check_budget(tenant_id: str) -> tuple[bool, str]:
    """Reject before starting an expensive AI workflow if the tenant's daily budget is exhausted."""
    budget = _budget_for(tenant_id)
    spent = spent_today_usd(tenant_id)
    if spent >= budget.daily_budget_usd:
        return False, f'Tenant daily AI budget exhausted (${spent:.2f} / ${budget.daily_budget_usd:.2f})'
    return True, ''


def record_usage(tenant_id: str, case_id: int | None, agent: str, model: str | None,
                  input_tokens: int, output_tokens: int, cost_usd: float, cost_basis: str = 'estimated',
                  request_id: str | None = None) -> None:
    try:
        with SessionLocal() as db:
            db.add(UsageRecord(
                tenant_id=tenant_id, case_id=case_id, agent=agent, model=model,
                input_tokens=input_tokens, output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens, cost_usd=cost_usd,
                cost_basis=cost_basis, request_id=request_id,
            ))
            db.commit()
    except Exception:
        log.exception('Failed to persist usage tenant=%s case=%s agent=%s',tenant_id,case_id,agent)
