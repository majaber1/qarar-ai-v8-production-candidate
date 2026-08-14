import {cookies} from 'next/headers';
import {devAutoLoginKey} from '../../../../lib/devAutoLogin';

const BACKEND=(process.env.BACKEND_URL??process.env.QARAR_BACKEND_URL??'http://127.0.0.1:8000/api').replace(/\/$/,'');

async function sessionKey(){
  const store=await cookies();
  return store.get('qarar_session_key')?.value || devAutoLoginKey();
}

async function proxy(req:Request,ctx:{params:Promise<{path:string[]}>}){
  const {path}=await ctx.params;
  const incoming=new URL(req.url);
  const target=new URL(`${BACKEND}/${path.join('/')}`);
  incoming.searchParams.forEach((v,k)=>target.searchParams.append(k,v));
  const key=await sessionKey();
  if(!key)return Response.json({detail:'Authentication required'},{status:401});

  const headers=new Headers();
  const contentType=req.headers.get('content-type');
  const accept=req.headers.get('accept');
  if(contentType)headers.set('content-type',contentType);
  if(accept)headers.set('accept',accept);
  headers.set('X-Qarar-API-Key',key);

  const init:any={method:req.method,headers,redirect:'manual',cache:'no-store'};
  if(!['GET','HEAD'].includes(req.method)){
    init.body=req.body;
    init.duplex='half';
  }
  let upstream:Response;
  try{
    upstream=await fetch(target,init);
  }catch(error){
    console.error('[qarar-proxy] backend unavailable',{path:target.pathname,error:error instanceof Error?error.message:String(error)});
    return Response.json({
      detail:'Qarar backend is unavailable',
      code:'BACKEND_UNAVAILABLE',
      retryable:true,
    },{status:503,headers:{'Cache-Control':'no-store','Retry-After':'30'}});
  }
  const outHeaders=new Headers();
  for(const name of ['content-type','cache-control','x-accel-buffering']){
    const value=upstream.headers.get(name); if(value)outHeaders.set(name,value);
  }
  return new Response(upstream.body,{status:upstream.status,headers:outHeaders});
}

export const GET=proxy;
export const POST=proxy;
export const PUT=proxy;
export const PATCH=proxy;
export const DELETE=proxy;
