import {cookies} from 'next/headers';
const BACKEND=(process.env.QARAR_BACKEND_URL??'http://127.0.0.1:8000/api').replace(/\/$/,'');
export async function POST(){const store=await cookies();const token=store.get('qarar_session_key')?.value;store.delete('qarar_session_key');if(token)await fetch(`${BACKEND}/auth/logout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})}).catch(()=>{});return Response.json({status:'ok'});}
