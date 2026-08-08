from app.services.agents.base import BaseAgent
from app.services.security_text import wrap_untrusted_content

class SpecialistAgent(BaseAgent):
    instructions=''; schema={}
    def execute(self,ctx):
        case_payload={k:v for k,v in ctx.case.__dict__.items() if k!='evidence_context'}
        payload={
            'case':case_payload,
            'retrieved_evidence':[
                {**hit, 'text': wrap_untrusted_content('retrieved-evidence', str(hit.get('text','')))}
                for hit in ctx.case.evidence_context
            ],
            'available_reports':{
                n:{'headline':r.headline,'summary':r.summary,'data':r.data,'confidence':r.confidence}
                for n,r in ctx.results.items()
            },
            'required_output':self.schema
        }
        data, usage = self.ask_json(ctx,self.instructions,payload)
        return self.mk(data, metadata={'usage': usage, 'estimated_cost_usd': usage.get('estimated_cost_usd',0.0)})
