import {cookies} from 'next/headers';
const BACKEND=(process.env.QARAR_BACKEND_URL??'http://127.0.0.1:8000/api').replace(/\/$/,'');
export async function POST(req:Request){
  const body=await req.json().catch(()=>({}));
  const key=String(body?.key||'').trim();
  let sessionKey=key,identity;
  if(body?.email&&body?.password&&body?.workspace_code){
    const login=await fetch(`${BACKEND}/auth/login`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:body.email,password:body.password,workspace_code:body.workspace_code}),cache:'no-store'});
    if(!login.ok)return Response.json(await login.json().catch(()=>({detail:'Invalid credentials'})),{status:login.status});
    const result=await login.json();sessionKey=result.token;identity=result.identity;
  }else{
    if(!key)return Response.json({detail:'Credentials required'},{status:400});
    const verify=await fetch(`${BACKEND}/whoami`,{headers:{'X-Qarar-API-Key':key},cache:'no-store'});
    if(!verify.ok)return Response.json({detail:'Invalid credentials'},{status:401});
    identity=await verify.json();
  }
  const store=await cookies();
  store.set('qarar_session_key',sessionKey,{httpOnly:true,sameSite:'strict',secure:process.env.NODE_ENV==='production',path:'/',maxAge:60*60*8});
  return Response.json(identity);
}
