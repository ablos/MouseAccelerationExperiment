import { db } from "$lib/server/db";
import { json } from "@sveltejs/kit";
import { sessions } from "$lib/server/db/schema.js";

export async function POST({ request, locals }) 
{
    const session = await request.json();
    
    const [{ sessionId }] = await db.insert(sessions).values(
        {
            participantId: locals.participantId,
            startTime: new Date(Date.now()),
            screenResX: session.screenResX,
            screenResY: session.screenResY,
            screenPxPerMm: session.pxPerMm,
            devicePixelRatio: session.devicePixelRatio,
            userAgent: session.userAgent,
            samePC: session.samePC,
            sameSetting: session.sameSetting,
            sameMouse: session.sameMouse,
            hoursSinceLastSession: session.hoursSinceLastSession
        }).returning({ sessionId: sessions.id });
        
    return json({ ok: true, sessionId });
}