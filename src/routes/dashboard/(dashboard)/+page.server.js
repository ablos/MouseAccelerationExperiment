import { db } from '$lib/server/db';
import { participants, participantContacts, sessions, studyConfig } from '$lib/server/db/schema';
import { eq, notInArray } from 'drizzle-orm';
import { getCurrentSlot } from '$lib/studySchedule.js';
import { redirect } from '@sveltejs/kit';
import { sendEmail } from '$lib/server/mailer.js';
import { reminderEmail } from '$lib/server/emails/reminder.js';

async function getPendingParticipants(slot)
{
    const doneSessions = await db
        .select({ participantId: sessions.participantId })
        .from(sessions)
        .where(eq(sessions.slot, slot));

    const doneIds = doneSessions.map(s => s.participantId);

    const query = db
        .select({
            id: participants.id,
            code: participants.code,
            name: participantContacts.name,
            email: participantContacts.email,
            phone: participantContacts.phone,
            afternoonReminderDate: participantContacts.afternoonReminderDate
        })
        .from(participants)
        .leftJoin(participantContacts, eq(participantContacts.participantId, participants.id));

    return doneIds.length
        ? await query.where(notInArray(participants.id, doneIds))
        : await query;
}

export async function load()
{
    const [config] = await db.select().from(studyConfig);
    const slot = getCurrentSlot(config);

    const pending = slot ? await getPendingParticipants(slot) : [];

    return { slot, pending };
}

export const actions =
{
    logout: async ({ cookies }) =>
    {
        cookies.delete('researcherAuth', { path: '/dashboard' });
        redirect(303, '/dashboard/login');
    },

    sendReminders: async () =>
    {
        const [config] = await db.select().from(studyConfig);
        const slot = getCurrentSlot(config);
        if (!slot) return { remindersSent: 0 };

        const todayISO = new Date().toISOString().slice(0, 10);

        const pending = await getPendingParticipants(slot);
        const withEmail = pending.filter(p => p.email && p.afternoonReminderDate !== todayISO);
        if (!withEmail.length) return { remindersSent: 0 };

        let remindersSent = 0;
        for (const p of withEmail)
        {
            try
            {
                await sendEmail({
                    to: p.email,
                    subject: 'Reminder: complete your session today',
                    html: reminderEmail(p.name, p.code, 'afternoon', p.id)
                });
                await db
                    .update(participantContacts)
                    .set({ afternoonReminderDate: todayISO })
                    .where(eq(participantContacts.participantId, p.id));
                remindersSent++;
            }
            catch (e)
            {
                console.error(`Failed to send reminder to participant ${p.id}:`, e.message);
            }
        }

        return { remindersSent };
    }
}
