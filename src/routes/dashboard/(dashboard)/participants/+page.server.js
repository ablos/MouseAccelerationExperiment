import { db } from '$lib/server/db';
import { participants, sessions } from '$lib/server/db/schema';

export async function load() 
{
    const allParticipants = await db.select().from(participants);
    const allSessions = await db.select({ participantId: sessions.participantId }).from(sessions);
    
    return { participants: allParticipants, sessions: allSessions };
}