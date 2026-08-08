import {cookies} from 'next/headers';
export async function POST(){const store=await cookies();store.delete('qarar_session_key');return Response.json({status:'ok'});}
