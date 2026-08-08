from importlib import import_module
SPECIALISTS=['evidence','policy','legal','risk','financial','strategy','stakeholder','timeline','cybersecurity','architecture','cloud','procurement','project_management','data_governance','compliance','business_continuity','operations','hr']
FLOW=['options','critic','chief_advisor']; NAMES=SPECIALISTS+FLOW
def cname(n):return ''.join(x.title() for x in n.split('_'))+'Agent'
class Registry:
 def __init__(self): self.agents={n:getattr(import_module(f'app.services.agents.{n}'),cname(n))() for n in NAMES}
 def get(self,n):return self.agents[n]
 def describe(self):return [{'name':n,'display_name_ar':a.display_name_ar,'dependencies':list(a.dependencies)} for n,a in self.agents.items()]
registry=Registry()
