from datetime import datetime, timezone
from typing import Any
from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AuditEvent(Base):
    """Append-only audit trail. No API route may update or delete rows in this table."""
    __tablename__ = 'audit_events_v6'
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(80), index=True)
    actor: Mapped[str] = mapped_column(String(200), index=True)
    auth_type: Mapped[str] = mapped_column(String(30), default='api_key')
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    resource_type: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    resource_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class UsageRecord(Base):
    """AI usage ledger. `actual` distinguishes provider-reported usage from `estimated` planning figures."""
    __tablename__ = 'usage_records_v6'
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(80), index=True)
    case_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    agent: Mapped[str] = mapped_column(String(80), index=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    cost_basis: Mapped[str] = mapped_column(String(20), default='estimated')  # 'estimated' | 'actual'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class CostBudget(Base):
    __tablename__ = 'cost_budgets_v6'
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    daily_budget_usd: Mapped[float] = mapped_column(Float, default=25.0)
    case_run_budget_usd: Mapped[float] = mapped_column(Float, default=2.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class MCPServerRegistration(Base):
    """Tenant-owned remote MCP server registry (Qarar acting as MCP client/gateway)."""
    __tablename__ = 'mcp_server_registrations_v6'
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(80), index=True)
    server_key: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(1000))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    auth_type: Mapped[str] = mapped_column(String(20), default='none')  # 'none' | 'bearer_env'
    auth_env_var: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tool_allowlist_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # null = allow all
    timeout_seconds: Mapped[float] = mapped_column(Float, default=20.0)
    last_health_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_health_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_health_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class ScanResult(Base):
    """Malware/security scan outcome for an uploaded object, recorded before a source becomes searchable."""
    __tablename__ = 'scan_results_v6'
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(80), index=True)
    source_id: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(20), index=True)  # 'clean' | 'infected' | 'scan_skipped' | 'scan_failed'
    engine: Mapped[str | None] = mapped_column(String(60), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    scanned_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
