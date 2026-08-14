from __future__ import annotations
from math import isfinite

DEFAULT_CRITERIA = [
    {'key':'compliance','name':'Compliance','description':'Fit with mandatory obligations','weight':.25},
    {'key':'risk','name':'Risk control','description':'Ability to reduce material risk','weight':.20},
    {'key':'financial','name':'Financial value','description':'Cost and expected value','weight':.15},
    {'key':'time','name':'Time to value','description':'Delivery speed and schedule fit','weight':.15},
    {'key':'strategy','name':'Strategic alignment','description':'Contribution to stated objectives','weight':.15},
    {'key':'stakeholder','name':'Stakeholder fit','description':'Adoption and stakeholder impact','weight':.10},
]
DEFAULT_WEIGHTS={x['key']:x['weight'] for x in DEFAULT_CRITERIA}

def _number(value):
    if value is None or isinstance(value,bool): return None
    try: result=float(value)
    except (TypeError,ValueError): return None
    return result if isfinite(result) else None

def normalize_weights(weights=None):
    candidate=weights or DEFAULT_WEIGHTS
    if not isinstance(candidate,dict) or not candidate: raise ValueError('Scoring weights must be a non-empty object')
    cleaned={}
    for key,weight in candidate.items():
        if key not in DEFAULT_WEIGHTS: raise ValueError(f'Unknown scoring criterion: {key}')
        number=_number(weight)
        if number is None or number<0: raise ValueError(f'Weight for {key} must be finite and non-negative')
        cleaned[key]=number
    total=sum(cleaned.values())
    if total<=0: raise ValueError('At least one scoring weight must be greater than zero')
    return {key:round(value/total,6) for key,value in cleaned.items()}

def normalize_criteria(criteria=None,weights=None):
    source=criteria or [{**item,'weight':(weights or {}).get(item['key'],item['weight'])} for item in DEFAULT_CRITERIA if not weights or item['key'] in weights]
    if not isinstance(source,list) or not source: raise ValueError('At least one scoring criterion is required')
    result=[]; seen=set()
    for raw in source:
        key=str(raw.get('key','')).strip()
        if not key or key in seen: raise ValueError('Criterion keys must be present and unique')
        seen.add(key)
        weight=_number(raw.get('weight')); low=_number(raw.get('scale_min',0)); high=_number(raw.get('scale_max',100))
        if weight is None or weight<0: raise ValueError(f'Invalid weight for {key}')
        if low is None or high is None or high<=low: raise ValueError(f'Invalid scale for {key}')
        direction=raw.get('direction','higher_better')
        if direction not in {'higher_better','lower_better'}: raise ValueError(f'Invalid direction for {key}')
        missing=raw.get('missing_policy','incomplete')
        if missing not in {'incomplete','exclude'}: raise ValueError(f'Invalid missing policy for {key}')
        result.append({'key':key,'name':str(raw.get('name') or key),'description':str(raw.get('description') or ''),'weight':weight,'scale_min':low,'scale_max':high,'direction':direction,'missing_policy':missing})
    total=sum(x['weight'] for x in result)
    if total<=0: raise ValueError('Total criterion weight must be greater than zero')
    for item in result: item['weight']=round(item['weight']/total,6)
    return result

def _normalized_score(raw,criterion):
    value=_number(raw)
    if value is None:return None
    low,high=criterion['scale_min'],criterion['scale_max']
    bounded=max(low,min(high,value)); normalized=(bounded-low)/(high-low)*100
    if criterion['direction']=='lower_better':normalized=100-normalized
    return round(normalized,4)

def score_options(options,weights=None,criteria=None,tie_threshold=0.01):
    configured=normalize_criteria(criteria,weights)
    output=[]
    for option in options:
        raw_scores=option.get('criterion_scores') if isinstance(option,dict) else {}
        raw_scores=raw_scores if isinstance(raw_scores,dict) else {}
        details=[]; missing_required=[]; numerator=denominator=0.0
        for criterion in configured:
            value=_normalized_score(raw_scores.get(criterion['key']),criterion)
            if value is None:
                if criterion['missing_policy']=='incomplete':missing_required.append(criterion['key'])
            else:
                numerator+=value*criterion['weight'];denominator+=criterion['weight']
            details.append({**criterion,'raw_score':raw_scores.get(criterion['key']),'normalized_score':value,'weighted_contribution':round(value*criterion['weight'],4) if value is not None else None})
        valid=not missing_required and denominator>0
        score=round(numerator/denominator,2) if valid else None
        item={**option,'criterion_details':details,'score_completeness':round(sum(x['normalized_score'] is not None for x in details)/len(details),4),'missing_criteria':missing_required,'score_valid':valid,'weighted_score':score,'calculation_metadata':{'method':'weighted-normalized-v2','normalized_weight_total':round(denominator,6),'missing_policy':'explicit','tie_threshold':tie_threshold}}
        output.append(item)
    output.sort(key=lambda x:(x['score_valid'],x['weighted_score'] if x['weighted_score'] is not None else -1),reverse=True)
    if len(output)>1 and output[0]['score_valid'] and output[1]['score_valid']:
        difference=round(output[0]['weighted_score']-output[1]['weighted_score'],2)
        output[0]['rank_status']='tied' if difference<=tie_threshold else 'leader'
        output[0]['lead_over_next']=difference
    for index,item in enumerate(output,1):item['rank']=index
    return output

def sensitivity_analysis(options,criteria,weight_changes=None,score_changes=None):
    configured=normalize_criteria(criteria)
    baseline=score_options(options,criteria=configured)
    changed=[]
    for criterion in configured:
        new=dict(criterion)
        if weight_changes and criterion['key'] in weight_changes:new['weight']=weight_changes[criterion['key']]
        changed.append(new)
    adjusted=[]
    for option in options:
        copy={**option,'criterion_scores':dict(option.get('criterion_scores') or {})}
        for key,value in (score_changes or {}).get(str(option.get('id')),{}).items():copy['criterion_scores'][key]=value
        adjusted.append(copy)
    scenario=score_options(adjusted,criteria=changed)
    before=baseline[0].get('id') if baseline and baseline[0].get('score_valid') else None
    after=scenario[0].get('id') if scenario and scenario[0].get('score_valid') else None
    margin=(scenario[0].get('lead_over_next') or 0) if scenario else 0
    stability='highly_sensitive' if before!=after or margin<2 else ('moderately_sensitive' if margin<8 else 'stable')
    return {'baseline':baseline,'scenario':scenario,'baseline_leader':before,'scenario_leader':after,'stability':stability,'changed_recommendation':before!=after,'note':'Sensitivity is directional, not a probability forecast.'}

def compose_confidence(evidence,scored_options,*,clarifications=None,assumptions=None,conflicts=None,sensitivity=None):
    facts=evidence.get('facts') or []; unknowns=evidence.get('missing_information') or []; sources=evidence.get('sources') or []
    context=len(facts)/(len(facts)+len(unknowns)) if facts or unknowns else 0
    coverage=min(1.0,len(sources)/3); trust={'A':1,'B':.8,'C':.55,'D':.25}
    quality=sum(trust.get(str(x.get('trust_level','C')).upper(),.4) for x in sources)/len(sources) if sources else 0
    completeness=sum(float(x.get('score_completeness',0)) for x in scored_options)/len(scored_options) if scored_options else 0
    valid=sorted([float(x['weighted_score']) for x in scored_options if x.get('score_valid')],reverse=True)
    differentiation=min(1,(valid[0]-valid[1])/20) if len(valid)>1 else 0
    clarification_factor=max(0,1-min(1,len(clarifications or unknowns)/5)); assumption_factor=max(0,1-min(1,len(assumptions or [])/5)); conflict_factor=max(0,1-min(1,len(conflicts or [])/3))
    stability={'stable':1,'moderately_sensitive':.6,'highly_sensitive':.2}.get((sensitivity or {}).get('stability'),.5)
    factors={'context_completeness':context,'evidence_coverage':coverage,'source_quality':quality,'scoring_completeness':completeness,'option_differentiation':differentiation,'clarification_resolution':clarification_factor,'assumption_control':assumption_factor,'conflict_control':conflict_factor,'sensitivity_stability':stability}
    weights={'context_completeness':.15,'evidence_coverage':.12,'source_quality':.12,'scoring_completeness':.18,'option_differentiation':.10,'clarification_resolution':.10,'assumption_control':.08,'conflict_control':.07,'sensitivity_stability':.08}
    value=round(sum(factors[k]*weights[k] for k in weights),2)
    positives=[k for k,v in factors.items() if v>=.75]; uncertainties=[k for k,v in factors.items() if v<.5]
    return value,{'method':'deterministic-v2','formula_weights':weights,'factors':{k:round(v,4) for k,v in factors.items()},'positive_factors':positives,'uncertainty_factors':uncertainties,'improvement_actions':[f'Improve {x.replace("_"," ")}' for x in uncertainties],'uncalibrated_model_confidence_excluded':True}
