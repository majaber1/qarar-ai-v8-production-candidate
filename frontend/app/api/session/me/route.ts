import {cookies} from 'next/headers';
import {devAutoLoginKey} from '../../../../lib/devAutoLogin';
const BACKEND=(process.env.BACKEND_URL??process.env.QARAR_BACKEND_URL??'http://127.0.0.1:8000/api').replace(/\/$/,'');
export async function GET(){
 const store=await cookies();const key=store.get('qarar_session_key')?.value||devAutoLoginKey();
 if(!key)return Response.json({detail:'Authentication required'},{status:401});
 try{
  const r=await fetch(`${BACKEND}/whoami`,{headers:{'X-Qarar-API-Key':key},cache:'no-store'});
  return new Response(r.body,{status:r.status,headers:{'content-type':r.headers.get('content-type')||'application/json'}});
 }catch(error){
  console.error('[session-me] backend unavailable',error instanceof Error?error.message:String(error));
  return Response.json({detail:'Qarar backend is unavailable',code:'BACKEND_UNAVAILABLE',retryable:true},{status:503,headers:{'Retry-After':'30'}});
 }
}
