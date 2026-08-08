from datetime import datetime,timezone
from sqlalchemy import DateTime,Integer,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from app.core.database import Base

class KnowledgeItem(Base):
    __tablename__='knowledge_items'
    id:Mapped[int]=mapped_column(primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(80),index=True)
    case_id:Mapped[int|None]=mapped_column(Integer,nullable=True,index=True)
    source_type:Mapped[str]=mapped_column(String(30),index=True)
    title:Mapped[str]=mapped_column(String(500))
    source_ref:Mapped[str|None]=mapped_column(String(1000),nullable=True)
    content:Mapped[str]=mapped_column(Text)
    metadata_json:Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
