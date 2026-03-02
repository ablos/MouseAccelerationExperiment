import { db } from '$lib/server/db';
import { sessions } from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';

export async function load({ locals }) 
{
    const existing = await db.select({ id: sessions.id }).from(sessions).where(eq(sessions.participantId, locals.participantId)).limit(1);
    
    return { isFirstSession: existing.length === 0 };
}