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
    scoring_criteria:Mapped[list[dict[str,Any]]|None]=mapped_column(JSON,nullable=True)
    calculation_metadata:Mapped[dict[str,Any]|None]=mapped_column(JSON,nullable=True)
    options:Mapped[list[dict[str,Any]]|None]=mapped_column(JSON,nullable=True)
    score_provenance:Mapped[dict[str,Any]|None]=mapped_column(JSON,nullable=True)
    override_history:Mapped[list[dict[str,Any]]|None]=mapped_column(JSON,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda: datetime.now(timezone.utc))
    updated_at:Mapped[datetime]=mapped_column(DateTime,default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))

class DecisionAction(Base):
    __tablename__='decision_actions_v83'
    id:Mapped[int]=mapped_column(primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(80),index=True)
    case_id:Mapped[int]=mapped_column(Integer,index=True)
    title:Mapped[str]=mapped_column(String(250))
    description:Mapped[str|None]=mapped_column(Text,nullable=True)
    owner:Mapped[str]=mapped_column(String(200),index=True)
    status:Mapped[str]=mapped_column(String(30),default='not_started',index=True)
    priority:Mapped[str]=mapped_column(String(20),default='medium',index=True)
    due_date:Mapped[date|None]=mapped_column(Date,nullable=True,index=True)
    dependency_id:Mapped[int|None]=mapped_column(Integer,nullable=True,index=True)
    created_by:Mapped[str]=mapped_column(String(200))
    source_reference:Mapped[str|None]=mapped_column(String(500),nullable=True)
    completion_date:Mapped[date|None]=mapped_column(Date,nullable=True)
    notes:Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
    updated_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),onupdate=lambda:datetime.now(timezone.utc))

class DecisionOutcome(Base):
    __tablename__='decision_outcomes_v83'
    id:Mapped[int]=mapped_column(primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(80),index=True)
    case_id:Mapped[int]=mapped_column(Integer,index=True)
    result:Mapped[str]=mapped_column(String(20),index=True)
    expected_result:Mapped[str]=mapped_column(Text)
    actual_result:Mapped[str]=mapped_column(Text)
    lessons_learned:Mapped[str|None]=mapped_column(Text,nullable=True)
    corrective_action:Mapped[str|None]=mapped_column(Text,nullable=True)
    next_review_date:Mapped[date|None]=mapped_column(Date,nullable=True,index=True)
    recorded_by:Mapped[str]=mapped_column(String(200))
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
