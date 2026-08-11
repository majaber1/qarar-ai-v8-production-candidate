const configuredBackend=process.env.QARAR_BACKEND_URL?.replace(/\/$/,'');

export async function GET(){
  if(!configuredBackend){
    return Response.json({
      status:'degraded',
      frontend:'ready',
      backend:'not_configured',
      missing:['QARAR_BACKEND_URL'],
    },{status:503,headers:{'Cache-Control':'no-store'}});
  }
  try{
    const response=await fetch(`${configuredBackend}/readyz`,{
      cache:'no-store',
      signal:AbortSignal.timeout(5000),
    });
    return Response.json({
      status:response.ok?'ready':'degraded',
      frontend:'ready',
      backend:response.ok?'ready':'not_ready',
    },{status:response.ok?200:503,headers:{'Cache-Control':'no-store'}});
  }catch(error){
    console.error('[deployment-health] backend unreachable',error instanceof Error?error.message:String(error));
    return Response.json({
      status:'degraded',
      frontend:'ready',
      backend:'unreachable',
    },{status:503,headers:{'Cache-Control':'no-store','Retry-After':'30'}});
  }
}
