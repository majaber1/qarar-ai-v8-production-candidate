'use client';
import {useEffect,useState} from 'react';
import {api,MCPServer} from '@/lib/api';
import {useLang} from '@/components/LanguageProvider';

export default function Page(){
  const{t}=useLang();
  const[data,setData]=useState<any>(null);
  const[servers,setServers]=useState<MCPServer[]>([]);
  const[showAdd,setShowAdd]=useState(false);
  const[name,setName]=useState('');
  const[url,setUrl]=useState('');
  const[apiKey,setApiKey]=useState('');
  const[busy,setBusy]=useState('');
  const[err,setErr]=useState('');

  async function load(){
    try{setData(await api.connectCatalog())}catch{}
    try{setServers(await api.mcpServers())}catch{}
  }
  useEffect(()=>{load()},[]);

  async function addServer(){
    if(!name||!url)return;
    setBusy('add');setErr('');
    try{
      await api.mcpRegister({name,url,api_key:apiKey||undefined});
      setName('');setUrl('');setApiKey('');setShowAdd(false);await load();
    }catch(e){setErr(String(e))}finally{setBusy('')}
  }

  async function toggle(s:MCPServer){
    setBusy(`toggle-${s.id}`);
    try{await api.mcpToggle(s.id,!s.enabled);await load()}catch(e){setErr(String(e))}finally{setBusy('')}
  }

  async function remove(s:MCPServer){
    setBusy(`del-${s.id}`);
    try{await api.mcpDelete(s.id);await load()}catch(e){setErr(String(e))}finally{setBusy('')}
  }

  async function healthCheck(s:MCPServer){
    setBusy(`health-${s.id}`);
    try{await api.mcpHealth(s.id);await load()}catch(e){setErr(String(e))}finally{setBusy('')}
  }

  return <main className="container">
    <div className="pageTitle"><span className="kicker">QARAR CONNECT</span>
      <h1>{t('طبقة ربط واحدة لكل أدواتك','One connection layer for every tool')}</h1>
      <p>{t('Qarar يعمل كخادم MCP وكعميل MCP، مع موصلات OAuth وخيارات جاهزة لـ Microsoft 365 وGitHub وGoogle وأي MCP بعيد.','Qarar is both an MCP server and MCP client, with OAuth-ready adapters for Microsoft 365, GitHub, Google, and any remote MCP.')}</p>
    </div>
    {err&&<div className="errorBox">{err}</div>}
    <div className="grid g3">
      {(data?.connectors||[]).map((x:any)=><div className="card" key={x.id}>
        <span className="badge gold">{x.status}</span>
        <h2>{x.name}</h2>
        <p className="muted">{(x.channels||[]).join(' · ')}</p>
        <b>{x.configured?t('مهيأ','Configured'):t('جاهز للتهيئة','Ready to configure')}</b>
      </div>)}
    </div>

    <div className="sectionHead">
      <div><span className="kicker">MCP SERVER REGISTRY</span>
        <h2>{t('خوادم MCP المسجلة','Registered MCP servers')}</h2>
      </div>
      <button className="btn gold" onClick={()=>setShowAdd(!showAdd)}>
        {showAdd?t('إلغاء','Cancel'):t('+ إضافة خادم','+ Add server')}
      </button>
    </div>

    {showAdd&&<div className="card mcpAddForm">
      <div className="g3" style={{gap:12}}>
        <div className="field"><label>{t('الاسم','Name')}</label>
          <input value={name} onChange={e=>setName(e.target.value)} placeholder="e.g. internal-tools"/></div>
        <div className="field"><label>URL</label>
          <input value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://mcp.example.com/sse"/></div>
        <div className="field"><label>API Key ({t('اختياري','optional')})</label>
          <input value={apiKey} onChange={e=>setApiKey(e.target.value)} placeholder="Bearer token"/></div>
      </div>
      <button className="btn gold" onClick={addServer} disabled={busy==='add'||!name||!url}>
        {busy==='add'?t('جارٍ التسجيل...','Registering...'):t('تسجيل','Register')}
      </button>
    </div>}

    <div className="mcpServerList">
      {(data?.mcp_servers||[]).map((x:any)=><div className="mcpServerRow system" key={`sys-${x.id}`}>
        <div className="mcpServerInfo"><b>{x.name}</b><small className="muted">{x.url}</small></div>
        <span className="badge">{t('نظام','System')}</span>
        <span className={`status ${x.enabled?'ok':'planned'}`}>{x.enabled?'ON':'OFF'}</span>
      </div>)}
      {servers.map(s=><div className="mcpServerRow" key={s.id}>
        <div className="mcpServerInfo"><b>{s.name}</b><small className="muted">{s.url}</small></div>
        <span className={`status ${s.health_status==='healthy'?'ok':s.health_status==='unhealthy'?'fail':'planned'}`}>
          {s.health_status||'unknown'}
        </span>
        <div className="mcpServerActions">
          <button className="btn soft" onClick={()=>healthCheck(s)} disabled={busy===`health-${s.id}`}>
            {busy===`health-${s.id}`?'...':t('فحص','Health')}
          </button>
          <button className="btn soft" onClick={()=>toggle(s)} disabled={busy===`toggle-${s.id}`}>
            {s.enabled?t('إيقاف','Disable'):t('تمكين','Enable')}
          </button>
          <button className="btn soft" style={{color:'#b65a5a'}} onClick={()=>remove(s)} disabled={busy===`del-${s.id}`}>
            {t('حذف','Delete')}
          </button>
        </div>
      </div>)}
      {!data?.mcp_servers?.length&&!servers.length&&<p className="muted">{t('لا توجد خوادم MCP مسجلة.','No MCP servers registered.')}</p>}
    </div>
  </main>
}
