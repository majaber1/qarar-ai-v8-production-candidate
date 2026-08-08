import {cookies} from 'next/headers';
import {devAutoLoginKey} from '../../../../lib/devAutoLogin';
const BACKEND=(process.env.QARAR_BACKEND_URL??'http://127.0.0.1:8000/api').replace(/\/$/,'');
export async function GET(){
 const store=await cookies();const key=store.get('qarar_session_key')?.value||devAutoLoginKey();
 if(!key)return Response.json({detail:'Authentication required'},{status:401});
 const r=await fetch(`${BACKEND}/whoami`,{headers:{'X-Qarar-API-Key':key},cache:'no-store'});
 return new Response(r.body,{status:r.status,headers:{'content-type':r.headers.get('content-type')||'application/json'}});
}
