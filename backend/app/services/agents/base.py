import json, time
from abc import ABC, abstractmethod
from app.services.contracts import AgentResult, ExecutionContext, Finding
from app.services.llm_client import LLMClient

AR='اكتب بالعربية الواضحة والبسيطة. تجنب اللغة الأكاديمية والمصطلحات الأجنبية غير الضرورية. اجعل الملخص من جملتين إلى ثلاث فقط.'

class BaseAgent(ABC):
    name='base'; display_name_ar='خبير'; description=''; dependencies=()

    def run(self, ctx):
        s=time.perf_counter()
        try:
            r=self.execute(ctx)
            r.duration_ms=int((time.perf_counter()-s)*1000)
            return r
        except Exception as e:
            return AgentResult(
                self.name,'failed','تعذر إكمال التحليل',
                'تعذر إكمال هذه الجزئية وسيستخدم النظام المسار الاحتياطي.',
                confidence=0,warnings=['agent_failed'],error=str(e),
                duration_ms=int((time.perf_counter()-s)*1000)
            )

    @abstractmethod
    def execute(self,ctx): ...

    MAX_JSON_ATTEMPTS = 2
    CORRECTIVE_INSTRUCTION = '\nReturn a JSON object matching the requested schema exactly. Do not return a JSON string, list, number, boolean, null, or markdown — only a single JSON object with the required keys.'

    def ask_json(self,ctx,instructions,payload):
        corrective=''
        usage_total={'input_tokens':0,'output_tokens':0,'total_tokens':0,'estimated_cost_usd':0.0}
        last_preview=''
        last_type='invalid_json'
        for _ in range(self.MAX_JSON_ATTEMPTS):
            raw, usage = LLMClient().generate_with_meta(
                instructions+corrective+'\n'+AR+'\nأعد JSON صالحًا فقط بدون Markdown.',
                json.dumps(payload,ensure_ascii=False)
            )
            for k in ('input_tokens','output_tokens','total_tokens'):
                usage_total[k]=usage_total.get(k,0)+int(usage.get(k,0) or 0)
            usage_total['estimated_cost_usd']=round(usage_total.get('estimated_cost_usd',0.0)+float(usage.get('estimated_cost_usd',0.0) or 0.0),6)
            cleaned=raw.strip().replace('```json','').replace('```','').strip()
            last_preview=cleaned[:200]
            try:
                parsed=json.loads(cleaned)
            except json.JSONDecodeError:
                parsed=None
            last_type=type(parsed).__name__ if parsed is not None else 'invalid_json'
            if isinstance(parsed,dict):
                return parsed, usage_total
            corrective=self.CORRECTIVE_INSTRUCTION
        raise ValueError(
            f'LLM did not return a JSON object after {self.MAX_JSON_ATTEMPTS} attempt(s); last response type={last_type}, preview={last_preview!r}'
        )

    def mk(self,d,metadata=None):
        fs=[Finding(str(x.get('label','')),str(x.get('detail','')),str(x.get('severity','info')),bool(x.get('verified',False))) for x in d.get('findings',[])]
        return AgentResult(
            self.name,str(d.get('status','success')),str(d.get('headline','')),str(d.get('summary','')),
            fs,d.get('data',{}),float(d.get('confidence',0)),[str(x) for x in d.get('warnings',[])],
            d.get('sources',[]),metadata=metadata or {}
        )
