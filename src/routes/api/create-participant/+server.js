import { db } from "$lib/server/db";
import { json } from "@sveltejs/kit";
import { participants } from "$lib/server/db/schema";

export async function POST({ request }) 
{
    const participant = await request.json();
    
    const [{ participantId }] = await db.insert(participants).values(
        {
        
        }).returning({ participantId: participants.id });
        
    return json({ ok: true, participantId });
}