from datetime import date,datetime
from typing import Any,Literal
from pydantic import BaseModel,ConfigDict,Field

class CaseCreate(BaseModel):
    project_id:int|None=None
    title:str=Field(min_length=3,max_length=250)
    description:str=Field(min_length=10)
    urgency:Literal['low','medium','high','critical']='medium'
    category:str|None=None
    language:Literal['ar','en']='ar'
    scoring_weights:dict[str,float]|None=None

class CaseUpdate(BaseModel):
    title:str|None=Field(default=None,min_length=3,max_length=250)
    description:str|None=Field(default=None,min_length=10)
    urgency:Literal['low','medium','high','critical']|None=None
    category:str|None=None
    project_id:int|None=None
    scoring_weights:dict[str,float]|None=None

class CaseTransitionRequest(BaseModel):
    status:Literal['archived','rejected','deferred','open']
    reason:str=Field(min_length=3,max_length=1000)

class ApprovalRequest(BaseModel):
    option_id:str
    decision_owner:str=Field(min_length=2)
    due_date:date|None=None

class CaseResponse(BaseModel):
    id:int
    tenant_id:str
    created_by:str
    project_id:int|None
    title:str
    description:str
    urgency:str
    category:str|None
    language:str
    status:str
    selected_agents:list[str]|None
    skipped_agents:list[str]|None
    agent_results:dict[str,Any]|None
    analysis:dict[str,Any]|None
    audit_log:list[dict[str,Any]]|None
    analysis_source:str|None
    approved_option:str|None
    decision_owner:str|None
    due_date:date|None
    pending_clarifications:list[str]|None=None
    clarification_answers:dict[str,Any]|None=None
    scoring_weights:dict[str,float]|None=None
    created_at:datetime
    updated_at:datetime
    model_config=ConfigDict(from_attributes=True)
