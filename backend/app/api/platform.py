from fastapi import APIRouter, Depends
from pydantic import BaseModel,Field
from app.core.auth import Principal, require_principal
from app.services.connectors import catalog as connector_catalog
from app.services.research import research_status
from app.core.config import settings

router=APIRouter(prefix='/platform',tags=['platform'])
PACKAGES=[
 {'id':'core','name':'Qarar Core','status':'active','features':['Dynamic council','Evidence-first reasoning','Selective agents','Live execution','Human decision gate']},
 {'id':'knowledge','name':'Qarar Knowledge','status':'active','features':['Object storage','Scalable ingestion','Chunking','Hybrid retrieval','Trust levels','Citations','Research modes']},
 {'id':'connect','name':'Qarar Connect','status':'active_foundation','features':['Authenticated Qarar remote MCP server','MCP client/gateway','Connector registry','OAuth-ready adapters','GitHub / M365 / Google / custom MCP']},
 {'id':'automate','name':'Qarar Automate','status':'active_foundation','features':['n8n webhook adapter','Dry-run','Server-verified human approval gate','Workflow catalog','Decision-to-action']},
 {'id':'enterprise','name':'Qarar Enterprise','status':'hardening','features':['Tenant isolation','API/MCP authentication','Role gates','Audit','Private deployment','Customer expert/source packs']},
]

class CostInput(BaseModel):
    users:int=Field(25,ge=1);decisions_per_month:int=Field(250,ge=1);avg_input_tokens:int=Field(7000,ge=100);avg_output_tokens:int=Field(2500,ge=100);input_usd_per_million:float=Field(1.25,ge=0);output_usd_per_million:float=Field(10,ge=0);avg_agent_calls:float=Field(4,ge=1);infra_monthly_usd:float=Field(150,ge=0);target_gross_margin_pct:float=Field(75,ge=1,le=95)

@router.get('/catalog')
def catalog(principal:Principal=Depends(require_principal)):
    return {'brand':{'name':'Qarar AI','category':'Enterprise Decision Intelligence Platform','promise':'Know. Decide. Act.','long_promise':'From Evidence to Decision to Action'},'packages':PACKAGES,'connectors':connector_catalog(),'research':research_status(),'mcp':{'server_url':settings.mcp_public_base_url.rstrip('/')+'/mcp','protocol':'MCP Streamable HTTP','server_process':'uvicorn app.mcp_server:app --port 8001'},'runtime':{'core':'active','knowledge':'active','connect':'authenticated-foundation','automate':'approval-enforced-foundation'}}

@router.post('/cost-estimate')
def cost(p:CostInput,principal:Principal=Depends(require_principal)):
    ai=p.decisions_per_month*p.avg_agent_calls*((p.avg_input_tokens/1e6*p.input_usd_per_million)+(p.avg_output_tokens/1e6*p.output_usd_per_million));total=ai+p.infra_monthly_usd;price=total/(1-p.target_gross_margin_pct/100)
    return {'currency':'USD','estimated_ai_cost':round(ai,2),'estimated_monthly_cogs':round(total,2),'cost_per_decision':round(total/p.decisions_per_month,3),'cost_per_user':round(total/p.users,2),'minimum_monthly_price_for_target_margin':round(price,2),'note':'Planning estimate. Replace token rates and infrastructure assumptions with contracted production rates.'}
