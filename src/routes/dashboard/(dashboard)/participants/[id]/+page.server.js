import { db } from '$lib/server/db';
import { participants, participantContacts, sessions } from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';

export async function load({ params }) 
{
    const { id } = params;

    const [participant] = await db.select().from(participants).where(eq(participants.id, id));
    const [contact] = await db.select().from(participantContacts).where(eq(participantContacts.participantId, id));
    const participantSessions = await db.select().from(sessions).where(eq(sessions.participantId, id));
    
    return { participant, contact, sessions: participantSessions };
}