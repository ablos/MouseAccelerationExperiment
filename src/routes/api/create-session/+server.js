import { db } from "$lib/server/db";
import { json } from "@sveltejs/kit";
import { sessions } from "$lib/server/db/schema.js";

export async function POST({ request }) 
{
    const session = await request.json();
    
    const [{ sessionId }] = await db.insert(sessions).values(
        {
            participantId: session.participantId,
            startTime: new Date(Date.now()),
            screenResX: session.screenResX,
            screenResY: session.screenResY,
            screenPxPerMm: session.pxPerMm
        }).returning({ sessionId: sessions.id });
        
    return json({ ok: true, sessionId });
}