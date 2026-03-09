import { db } from '$lib/server/db';
import { participants, participantContacts, sessions, studyConfig } from '$lib/server/db/schema';
import { eq, notInArray } from 'drizzle-orm';
import { getCurrentSlot } from '$lib/studySchedule.js';
import { redirect } from '@sveltejs/kit';
import { Resend } from 'resend';
import { env } from '$env/dynamic/private';
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
            phone: participantContacts.phone
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

        const pending = await getPendingParticipants(slot);
        const withEmail = pending.filter(p => p.email);
        if (!withEmail.length) return { remindersSent: 0 };

        const resend = new Resend(env.RESEND_API_KEY);
        await Promise.allSettled(
            withEmail.map(p =>
                resend.emails.send({
                    from: 'Mouse Acceleration Study <mouse-study@ablos.nl>',
                    to: p.email,
                    subject: 'Reminder: complete your session today',
                    html: reminderEmail(p.name, p.code, 'afternoon', p.id)
                })
            )
        );

        return { remindersSent: withEmail.length };
    }
}
