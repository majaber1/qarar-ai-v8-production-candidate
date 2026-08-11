from datetime import date,datetime,timezone
from typing import Any
from sqlalchemy import JSON,Date,DateTime,Integer,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from app.core.database import Base

class DecisionCase(Base):
    __tablename__='decision_cases'
    id:Mapped[int]=mapped_column(primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(80),index=True)
    created_by:Mapped[str]=mapped_column(String(200),index=True)
    project_id:Mapped[int|None]=mapped_column(Integer,nullable=True,index=True)
    title:Mapped[str]=mapped_column(String(250))
    description:Mapped[str]=mapped_column(Text)
    urgency:Mapped[str]=mapped_column(String(30),default='medium')
    category:Mapped[str|None]=mapped_column(String(80),nullable=True)
    language:Mapped[str]=mapped_column(String(10),default='ar')
    status:Mapped[str]=mapped_column(String(40),default='open')
    selected_agents:Mapped[list[str]|None]=mapped_column(JSON,nullable=True)
    skipped_agents:Mapped[list[str]|None]=mapped_column(JSON,nullable=True)
    agent_results:Mapped[dict[str,Any]|None]=mapped_column(JSON,nullable=True)
    analysis:Mapped[dict[str,Any]|None]=mapped_column(JSON,nullable=True)
    audit_log:Mapped[list[dict[str,Any]]|None]=mapped_column(JSON,nullable=True)
    analysis_source:Mapped[str|None]=mapped_column(String(30),nullable=True)
    approved_option:Mapped[str|None]=mapped_column(String(20),nullable=True)
    decision_owner:Mapped[str|None]=mapped_column(String(200),nullable=True)
    due_date:Mapped[date|None]=mapped_column(Date,nullable=True)
    pending_clarifications:Mapped[list[str]|None]=mapped_column(JSON,nullable=True)
    clarification_answers:Mapped[dict[str,Any]|None]=mapped_column(JSON,nullable=True)
    scoring_weights:Mapped[dict[str,float]|None]=mapped_column(JSON,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda: datetime.now(timezone.utc))
    updated_at:Mapped[datetime]=mapped_column(DateTime,default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))
