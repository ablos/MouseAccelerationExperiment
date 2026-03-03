import { db } from '$lib/server/db';
import { participants, participantContacts, sessions, studyConfig, tasks, trials, mouseCoordinates } from '$lib/server/db/schema';
import { eq, inArray } from 'drizzle-orm';
import { fail } from '@sveltejs/kit';

export async function load({ params }) 
{
    const { id } = params;

    const [participant] = await db.select().from(participants).where(eq(participants.id, id));
    const [contact] = await db.select().from(participantContacts).where(eq(participantContacts.participantId, id));
    const participantSessions = await db.select().from(sessions).where(eq(sessions.participantId, id));
    const [config] = await db.select().from(studyConfig);
    const sessionIds = participantSessions.map(s => s.id);
    
    const base = { participant, contact, sessions: participantSessions, config };

    if (!sessionIds.length)
        return { ...base, tasks: [], trials: [], mouseCoordinates: [] };

    const participantTasks = await db.select().from(tasks).where(inArray(tasks.sessionId, sessionIds));
    const taskIds = participantTasks.map(t => t.id);

    if (!taskIds.length)
        return { ...base, tasks: participantTasks, trials: [], mouseCoordinates: [] };

    const participantTrials = await db.select().from(trials).where(inArray(trials.taskId, taskIds));
    const trialIds = participantTrials.map(t => t.id);

    if (!trialIds.length)
        return { ...base, tasks: participantTasks, trials: participantTrials, mouseCoordinates: [] };

    const coords = await db.select().from(mouseCoordinates).where(inArray(mouseCoordinates.trialId, trialIds));

    return { ...base, tasks: participantTasks, trials: participantTrials, mouseCoordinates: coords };
}

export const actions = {
    updateContact: async ({ request }) => {
        const data = await request.formData();
        const id = data.get('participant-id')?.toString().trim() || null;
        const name = data.get('name')?.toString().trim() || null;
        const email = data.get('email')?.toString().trim() || null;
        const phone = data.get('phone')?.toString().trim() || null;
        const notes = data.get('notes')?.toString().trim() || null;
        
        // Check if participant exists
        const existingParticipant = await db.select({ participantId: participants.id }).from(participants).where(eq(participants.id, id));
        
        if (!existingParticipant.length) 
        {
            return fail(400, { error: 'This participant does not exist ' });
        }
        
        const existingContact = await db.select({ participantId: participantContacts.participantId }).from(participantContacts).where(eq(participantContacts.participantId, id));
        
        if (existingContact.length) 
        {
            await db.update(participantContacts).set(
            {
                participantId: id,
                name,
                email,
                phone,
                notes
            }).where(eq(participantContacts.participantId, id));
        }
        else 
        {
            await db.insert(participantContacts).values(
            {
                participantId: id,
                name,
                email,
                phone,
                notes
            });
        }
        
        return { success: true };
    }
}