import {cookies} from 'next/headers';
const BACKEND=(process.env.QARAR_BACKEND_URL??'http://127.0.0.1:8000/api').replace(/\/$/,'');
export async function POST(req:Request){
  const body=await req.json().catch(()=>({}));
  const key=String(body?.key||'').trim();
  if(!key)return Response.json({detail:'API key required'},{status:400});
  const verify=await fetch(`${BACKEND}/whoami`,{headers:{'X-Qarar-API-Key':key},cache:'no-store'});
  if(!verify.ok)return Response.json({detail:'Invalid credentials'},{status:401});
  const identity=await verify.json();
  const store=await cookies();
  store.set('qarar_session_key',key,{httpOnly:true,sameSite:'strict',secure:process.env.NODE_ENV==='production',path:'/',maxAge:60*60*8});
  return Response.json(identity);
}
