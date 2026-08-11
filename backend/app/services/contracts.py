from dataclasses import dataclass,field,asdict
from typing import Any
@dataclass
class Finding: label:str; detail:str; severity:str='info'; verified:bool=False
@dataclass
class AgentResult:
 agent_name:str; status:str; headline:str; summary:str; findings:list[Finding]=field(default_factory=list); data:dict[str,Any]=field(default_factory=dict); confidence:float=0.0; warnings:list[str]=field(default_factory=list); sources:list[dict[str,Any]]=field(default_factory=list); duration_ms:int=0; error:str|None=None; metadata:dict[str,Any]=field(default_factory=dict)
 def to_dict(self): return asdict(self)
@dataclass
class CaseInput:
 case_id:int|None; title:str; description:str; urgency:str; category:str|None=None; language:str='ar'; tenant_id:str='default'; evidence_context:list[dict[str,Any]]=field(default_factory=list); scoring_weights:dict[str,float]|None=None
@dataclass
class ExecutionContext: case:CaseInput; results:dict[str,AgentResult]=field(default_factory=dict); response_language:str='ar'
