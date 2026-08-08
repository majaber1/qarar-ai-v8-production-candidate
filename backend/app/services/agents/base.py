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

    def ask_json(self,ctx,instructions,payload):
        raw, usage = LLMClient().generate_with_meta(
            instructions+'\n'+AR+'\nأعد JSON صالحًا فقط بدون Markdown.',
            json.dumps(payload,ensure_ascii=False)
        )
        cleaned=raw.strip().replace('```json','').replace('```','').strip()
        return json.loads(cleaned), usage

    def mk(self,d,metadata=None):
        fs=[Finding(str(x.get('label','')),str(x.get('detail','')),str(x.get('severity','info')),bool(x.get('verified',False))) for x in d.get('findings',[])]
        return AgentResult(
            self.name,str(d.get('status','success')),str(d.get('headline','')),str(d.get('summary','')),
            fs,d.get('data',{}),float(d.get('confidence',0)),[str(x) for x in d.get('warnings',[])],
            d.get('sources',[]),metadata=metadata or {}
        )
