import { db } from '$lib/server/db';
import { sessions, studyConfig, participants } from '$lib/server/db/schema';
import { and, eq } from 'drizzle-orm';
import { getCurrentSlot, getNextSlotDate } from '$lib/studySchedule.js';
import { redirect } from '@sveltejs/kit';

export async function load({ locals }) 
{
    const existing = await db.select({ id: sessions.id }).from(sessions).where(eq(sessions.participantId, locals.participantId)).limit(1);
    const [config] = await db.select().from(studyConfig);
    
    if (!config || !config.startDate || !config.endDate)
        redirect(303, '/?reason=study-not-started');
        
    const slot = getCurrentSlot(config);
    
    if (!slot) 
    {
        const nextSlotDate = getNextSlotDate(config);
        redirect(303, nextSlotDate ? `/?reason=no-slot&next=${nextSlotDate.toISOString().slice(0, 10)}`
            : '/?reason=study-ended');
    }
    
    const [slotSession] = await db.select({ id: sessions.id }).from(sessions).where(and(
        eq(sessions.participantId, locals.participantId),
        eq(sessions.slot, slot)
    ));
    
    if (slotSession)
    {
        const nextSlotDate = getNextSlotDate(config);
        redirect(303, nextSlotDate ? `/?reason=slot-done&next=${nextSlotDate.toISOString().slice(0, 10)}`
            : '/?reason=slot-done');
    }

    if (slot > 1)
    {
        const [participant] = await db.select({ group: participants.group }).from(participants).where(eq(participants.id, locals.participantId));
        if (!participant?.group)
            redirect(303, '/?reason=no-group');
    }

    return { isFirstSession: existing.length === 0, slot };
}