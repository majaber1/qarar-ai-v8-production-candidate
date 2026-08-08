WEIGHTS={'compliance':.25,'risk':.20,'financial':.15,'time':.15,'strategy':.15,'stakeholder':.10}
def clamp(v):
 try:return max(0,min(100,float(v)))
 except:return 0
def score_options(options):
 out=[]
 for o in options:
  c=o.get('criterion_scores',{});x=dict(o);x['weighted_score']=round(sum(clamp(c.get(k,0))*w for k,w in WEIGHTS.items()),2);x['score_weights']=WEIGHTS;out.append(x)
 return sorted(out,key=lambda x:x['weighted_score'],reverse=True)
