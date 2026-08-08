from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class DecisionApproval(Base):
    __tablename__ = 'decision_approvals_v51'
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(80), index=True)
    case_id: Mapped[int] = mapped_column(Integer, index=True)
    option_id: Mapped[str] = mapped_column(String(40))
    decision_owner: Mapped[str] = mapped_column(String(200))
    approved_by: Mapped[str] = mapped_column(String(200), index=True)
    status: Mapped[str] = mapped_column(String(30), default='approved', index=True)
    approved_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class AutomationCallbackReceipt(Base):
    __tablename__ = 'automation_callback_receipts_v8'
    __table_args__ = (UniqueConstraint('nonce', name='uq_automation_callback_nonce_v8'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(Integer, index=True)
    nonce: Mapped[str] = mapped_column(String(128))
    received_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
