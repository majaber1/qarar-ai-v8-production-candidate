from datetime import datetime,timezone
from sqlalchemy import DateTime,Float,Integer,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from app.core.database import Base

class KnowledgeSource(Base):
    __tablename__='knowledge_sources_v5'
    id:Mapped[int]=mapped_column(primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(80),default='default',index=True)
    case_id:Mapped[int|None]=mapped_column(Integer,nullable=True,index=True)
    source_type:Mapped[str]=mapped_column(String(40),index=True)
    title:Mapped[str]=mapped_column(String(500))
    source_ref:Mapped[str|None]=mapped_column(String(1500),nullable=True)
    object_key:Mapped[str|None]=mapped_column(String(1500),nullable=True)
    trust_level:Mapped[str]=mapped_column(String(2),default='B',index=True)
    status:Mapped[str]=mapped_column(String(30),default='queued',index=True)
    metadata_json:Mapped[str|None]=mapped_column(Text,nullable=True)
    error:Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))

class KnowledgeChunk(Base):
    __tablename__='knowledge_chunks_v5'
    id:Mapped[int]=mapped_column(primary_key=True)
    source_id:Mapped[int]=mapped_column(Integer,index=True)
    tenant_id:Mapped[str]=mapped_column(String(80),default='default',index=True)
    case_id:Mapped[int|None]=mapped_column(Integer,nullable=True,index=True)
    chunk_index:Mapped[int]=mapped_column(Integer)
    content:Mapped[str]=mapped_column(Text)
    embedding_json:Mapped[str|None]=mapped_column(Text,nullable=True)
    metadata_json:Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))

class AutomationRun(Base):
    __tablename__='automation_runs_v5'
    id:Mapped[int]=mapped_column(primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(80),index=True)
    actor:Mapped[str|None]=mapped_column(String(200),nullable=True,index=True)
    case_id:Mapped[int|None]=mapped_column(Integer,nullable=True,index=True)
    workflow_id:Mapped[str]=mapped_column(String(120),index=True)
    status:Mapped[str]=mapped_column(String(30),default='pending')
    approved:Mapped[int]=mapped_column(Integer,default=0)
    dry_run:Mapped[int]=mapped_column(Integer,default=1)
    input_json:Mapped[str|None]=mapped_column(Text,nullable=True)
    result_json:Mapped[str|None]=mapped_column(Text,nullable=True)
    error:Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
