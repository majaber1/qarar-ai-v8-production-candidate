const BASE = "/api/qarar";

export type QCase = {
  id:number; project_id?:number; title:string; description:string; urgency:string; category?:string; language?:string; status:string;
  selected_agents?:string[]; skipped_agents?:string[]; agent_results?:Record<string,any>; analysis?:Record<string,any>;
  audit_log?:any[]; analysis_source?:string; approved_option?:string; decision_owner?:string; due_date?:string;
  pending_clarifications?:string[]; clarification_answers?:Record<string,string>;
  created_at:string; updated_at:string;
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
  list:()=>req('/cases'),
  get:(id:string)=>req(`/cases/${id}`),
  create:(x:any)=>req('/cases',{method:'POST',body:JSON.stringify(x)}),
  analyze:(id:string)=>req(`/cases/${id}/analyze`,{method:'POST'}),
  approve:(id:string,x:any)=>req(`/cases/${id}/approve`,{method:'POST',body:JSON.stringify(x)}),
  clarify:(id:string,answers:Record<string,string>)=>req(`/cases/${id}/clarify`,{method:'POST',body:JSON.stringify({answers})}),

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

  // Readiness
  readyz:()=>req('/readyz'),
};
