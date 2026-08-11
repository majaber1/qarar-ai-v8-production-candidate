const BACKEND=(process.env.QARAR_BACKEND_URL??'http://127.0.0.1:8000/api').replace(/\/$/,'');
export async function POST(req:Request){
  const body=await req.json().catch(()=>({}));
  try{
    const response=await fetch(`${BACKEND}/auth/register`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),cache:'no-store'});
    return Response.json(await response.json().catch(()=>({detail:'Registration service unavailable'})),{status:response.status});
  }catch(error){
    console.error('[session-register] backend unavailable',error instanceof Error?error.message:String(error));
    return Response.json({detail:'Qarar backend is unavailable',code:'BACKEND_UNAVAILABLE',retryable:true},{status:503,headers:{'Retry-After':'30'}});
  }
}
