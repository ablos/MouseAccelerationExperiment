import { db } from '$lib/server/db';
import { participants, participantContacts, sessions, studyConfig } from '$lib/server/db/schema';
import { and, eq, notInArray } from 'drizzle-orm';
import { env } from '$env/dynamic/private';
import { sendEmail } from '$lib/server/mailer.js';
import { reminderEmail } from '$lib/server/emails/reminder.js';
import { getCurrentSlot } from '$lib/studySchedule.js';
import { json } from '@sveltejs/kit';

export async function GET({ url })
{
    const secret = url.searchParams.get('secret');
    if (!secret || secret !== env.CRON_SECRET)
        return new Response('Unauthorized', { status: 401 });

    const type = url.searchParams.get('type');
    if (type !== 'morning' && type !== 'afternoon')
        return new Response('Invalid type', { status: 400 });

    const [config] = await db.select().from(studyConfig);
    const slot = getCurrentSlot(config);

    if (!slot)
        return json({ sent: 0, reason: 'Not a session day' });

    // Find participant IDs that already have a session for this slot
    const completedSessions = await db
        .select({ participantId: sessions.participantId })
        .from(sessions)
        .where(eq(sessions.slot, slot));

    const completedIds = completedSessions.map(s => s.participantId);

    // Get all contacts who have email reminders enabled and haven't started this slot
    const baseCondition = eq(participantContacts.emailReminders, true);
    const condition = completedIds.length
        ? and(baseCondition, notInArray(participantContacts.participantId, completedIds))
        : baseCondition;

    const contacts = await db
        .select({
            participantId: participantContacts.participantId,
            name: participantContacts.name,
            email: participantContacts.email,
            code: participants.code
        })
        .from(participantContacts)
        .innerJoin(participants, eq(participants.id, participantContacts.participantId))
        .where(condition);

    const withEmail = contacts.filter(c => c.email);

    if (!withEmail.length)
        return json({ sent: 0, reason: 'No pending participants with email' });

    const subject = type === 'morning'
        ? 'Reminder: today is a session day'
        : 'Last reminder: complete your session today';

    const results = await Promise.allSettled(
        withEmail.map(c =>
            sendEmail({
                to: c.email,
                subject,
                html: reminderEmail(c.name, c.code, type, c.participantId)
            })
        )
    );

    const sent = results.filter(r => r.status === 'fulfilled').length;
    const failed = results.filter(r => r.status === 'rejected').length;

    return json({ sent, failed });
}
