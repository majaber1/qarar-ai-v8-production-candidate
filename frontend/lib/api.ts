const BASE = "/api/qarar";

export type ScoringCriterion = {
  key: string;
  name: string;
  description?: string;
  weight: number;
  scale_min?: number;
  scale_max?: number;
  direction?: 'higher_better' | 'lower_better';
  missing_policy?: 'incomplete' | 'exclude';
  is_gate?: boolean;
  gate_min?: number | null;
  gate_max?: number | null;
  evidence_requirement?: string | null;
};

export type DecisionOption = {
  id: string;
  title: string;
  description?: string;
  benefits?: string[];
  risks?: string[];
  conditions?: string[];
  criterion_scores?: Record<string, number>;
  criterion_provenance?: Record<string, any>;
  weighted_score?: number | null;
  rank?: number;
  is_disqualified?: boolean;
  disqualification_reason?: string | null;
  gate_failures?: any[];
  status?: string;
  criterion_details?: any[];
};

export type ScoreProvenance = {
  criterion_key: string;
  criterion_name: string;
  raw_score: number;
  normalized_score: number;
  weighted_contribution: number;
  weight: number;
  weight_percentage: number;
  direction: string;
  scale_min: number;
  scale_max: number;
  rationale: string;
  evidence_references: string[];
  source_ids: any[];
  trust_level: string;
  evidence_coverage: string;
  confidence: number;
  assumptions: string[];
  missing_evidence: string[];
  assessment_method: string;
  assessment_source: 'AI' | 'HUMAN' | 'DETERMINISTIC';
  original_assessment?: string;
  original_score?: number;
  review_history?: any[];
  override_history?: any[];
  actor: string;
  timestamp: string;
  is_gate: boolean;
  gate_passed: boolean;
  gate_failure_reason?: string | null;
};

export type OverrideEntry = {
  option_id: string;
  criterion_key: string;
  criterion_name: string;
  previous_score: number;
  new_score: number;
  reason: string;
  actor: string;
  timestamp: string;
};

export type DecisionTemplate = {
  id: string;
  title_ar: string;
  title_en: string;
  category: string;
  description_ar: string;
  description_en: string;
  criteria: ScoringCriterion[];
  default_options: { id: string; title: string; description: string }[];
  clarification_questions: string[];
};

export type ScenarioPreset = {
  preset_id?: string;
  id?: string;
  title_ar: string;
  title_en: string;
  description_ar: string;
  description_en: string;
  weights?: Record<string, number>;
  baseline_leader?: string;
  scenario_leader?: string;
  leader_changed?: boolean;
  stability?: string;
  margin?: number;
  explanation_ar?: string;
  explanation_en?: string;
  baseline_ranking?: any[];
  scenario_ranking?: any[];
};

export type QCase = {
  id: number;
  project_id?: number;
  title: string;
  description: string;
  urgency: string;
  category?: string;
  language?: string;
  status: string;
  selected_agents?: string[];
  skipped_agents?: string[];
  agent_results?: Record<string, any>;
  analysis?: Record<string, any>;
  audit_log?: any[];
  analysis_source?: string;
  approved_option?: string;
  decision_owner?: string;
  due_date?: string;
  pending_clarifications?: string[];
  clarification_answers?: Record<string, string>;
  scoring_weights?: Record<string, number>;
  scoring_criteria?: ScoringCriterion[];
  calculation_metadata?: Record<string, any>;
  options?: DecisionOption[];
  score_provenance?: Record<string, ScoreProvenance>;
  override_history?: OverrideEntry[];
  created_at: string;
  updated_at: string;
};

export type QProject={id:number;name:string;objective:string;owner:string;status:string;created_at:string;updated_at:string};

export type MCPServer = {
  id:number; name:string; url:string; enabled:boolean; health_status?:string;
  last_health_check?:string; tool_allowlist?:string[];
};

export type AuditEvent = {
  id:number; tenant_id:string; actor:string; action:string; auth_type?:string;
  resource_type?:string; resource_id?:number; metadata?:Record<string,any>; created_at:string;
};

async function req(path:string, init?:RequestInit){
  const r = await fetch(BASE + path, {
    ...init,
    headers:{"Content-Type":"application/json", ...(init?.headers||{})},
    cache:"no-store"
  });
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function streamAnalyze(id:string,onEvent:(e:any)=>void){
  const r=await fetch(`${BASE}/cases/${id}/analyze-stream`,{method:'POST',headers:{Accept:'application/x-ndjson'}});
  if(!r.ok) throw new Error(await r.text());
  if(!r.body) throw new Error('Streaming response unavailable');
  const reader=r.body.getReader(),dec=new TextDecoder(); let buf='';
  while(true){
    const {value,done}=await reader.read(); if(done) break;
    buf+=dec.decode(value,{stream:true}); const lines=buf.split('\n'); buf=lines.pop()||'';
    for(const line of lines) if(line.trim()) onEvent(JSON.parse(line));
  }
  if(buf.trim()) onEvent(JSON.parse(buf));
}

export const api = {
  projects:():Promise<QProject[]>=>req('/projects'),
  project:(id:string)=>req(`/projects/${id}`),
  createProject:(x:{name:string;objective:string;owner:string})=>req('/projects',{method:'POST',body:JSON.stringify(x)}),
  accessRequests:()=>req('/access-requests'),
  approveAccess:(id:number)=>req(`/access-requests/${id}/approve`,{method:'POST'}),
  profile:()=>req('/profile'),
  updateProfile:(full_name:string)=>req('/profile',{method:'PATCH',body:JSON.stringify({full_name})}),
  changePassword:(current_password:string,new_password:string)=>req('/profile/password',{method:'POST',body:JSON.stringify({current_password,new_password})}),
  list:():Promise<QCase[]>=>req('/cases'),
  get:(id:string):Promise<QCase>=>req(`/cases/${id}`),
  create:(x:any):Promise<QCase>=>req('/cases',{method:'POST',body:JSON.stringify(x)}),
  update:(id:string,x:any):Promise<QCase>=>req(`/cases/${id}`,{method:'PATCH',body:JSON.stringify(x)}),
  transition:(id:string,status:string,reason:string):Promise<QCase>=>req(`/cases/${id}/transition`,{method:'POST',body:JSON.stringify({status,reason})}),
  analyze:(id:string):Promise<QCase>=>req(`/cases/${id}/analyze`,{method:'POST'}),
  approve:(id:string,x:any):Promise<QCase>=>req(`/cases/${id}/approve`,{method:'POST',body:JSON.stringify(x)}),
  clarify:(id:string,answers:Record<string,string>):Promise<QCase>=>req(`/cases/${id}/clarify`,{method:'POST',body:JSON.stringify({answers})}),
  sensitivity:(id:string,weight_changes:Record<string,number>)=>req(`/cases/${id}/sensitivity`,{method:'POST',body:JSON.stringify({weight_changes,score_changes:{}})}),
  templates:():Promise<DecisionTemplate[]>=>req('/cases/templates'),
  scenarioPresets:():Promise<ScenarioPreset[]>=>req('/cases/scenarios/presets'),
  overrideScore:(caseId:string,payload:{option_id:string;criterion_key:string;new_score:number;reason:string}):Promise<QCase>=>req(`/cases/${caseId}/override`,{method:'POST',body:JSON.stringify(payload)}),
  provenance:(caseId:string,optionId:string,criterionKey:string):Promise<ScoreProvenance>=>req(`/cases/${caseId}/provenance/${optionId}/${criterionKey}`),
  actions:(id:string)=>req(`/cases/${id}/actions`),
  createAction:(id:string,x:any)=>req(`/cases/${id}/actions`,{method:'POST',body:JSON.stringify(x)}),
  updateAction:(id:string,actionId:number,x:any)=>req(`/cases/${id}/actions/${actionId}`,{method:'PATCH',body:JSON.stringify(x)}),
  outcomes:(id:string)=>req(`/cases/${id}/outcomes`),
  createOutcome:(id:string,x:any)=>req(`/cases/${id}/outcomes`,{method:'POST',body:JSON.stringify(x)}),

  // Knowledge (V4 compat)
  items:(caseId?:string)=>req(`/knowledge/items${caseId?`?case_id=${caseId}`:''}`),
  emailStatus:()=>req('/knowledge/email/status'),
  syncEmail:(caseId?:string)=>req(`/knowledge/email/sync${caseId?`?case_id=${caseId}`:''}`,{method:'POST'}),
  ask:(x:any)=>req('/knowledge/ask',{method:'POST',body:JSON.stringify(x)}),
  upload:async(file:File,caseId?:string)=>{
    const fd=new FormData(); fd.append('file',file); if(caseId) fd.append('case_id',caseId);
    const r=await fetch(`${BASE}/knowledge/upload`,{method:'POST',body:fd});
    if(!r.ok) throw new Error(await r.text()); return r.json();
  },

  // Knowledge Fabric
  fabricSources:(caseId?:string,projectId?:string)=>req(`/fabric/sources?${new URLSearchParams({...caseId?{case_id:caseId}:{},...projectId?{project_id:projectId}:{}})}`),
  fabricAsk:(x:any)=>req('/fabric/ask',{method:'POST',body:JSON.stringify(x)}),
  fabricUpload:async(file:File,caseId?:string,trust='B',projectId?:string)=>{
    const fd=new FormData(); fd.append('file',file); fd.append('trust_level',trust); if(caseId) fd.append('case_id',caseId); if(projectId)fd.append('project_id',projectId);
    const r=await fetch(`${BASE}/fabric/upload`,{method:'POST',body:fd});
    if(!r.ok) throw new Error(await r.text()); return r.json();
  },

  // Connect + MCP registry
  connectCatalog:()=>req('/connect/catalog'),
  mcpServers:():Promise<MCPServer[]>=>req('/connect/mcp/servers'),
  mcpRegister:(x:any)=>req('/connect/mcp/servers',{method:'POST',body:JSON.stringify(x)}),
  mcpToggle:(id:number,enabled:boolean)=>req(`/connect/mcp/servers/${id}`,{method:'PATCH',body:JSON.stringify({enabled})}),
  mcpDelete:(id:number)=>req(`/connect/mcp/servers/${id}`,{method:'DELETE'}),
  mcpHealth:(id:number)=>req(`/connect/mcp/${id}/health`,{method:'POST'}),

  // Automation
  platformCatalog:()=>req('/platform/catalog'),
  runAutomation:(x:any)=>req('/connect/automation/run',{method:'POST',body:JSON.stringify(x)}),
  auditEvents:():Promise<AuditEvent[]>=>req('/connect/audit'),

  // Readiness
  readyz:()=>req('/readyz'),
};
