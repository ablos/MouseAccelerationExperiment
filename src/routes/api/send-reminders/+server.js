import { db } from '$lib/server/db';
import { participants, participantContacts, sessions, studyConfig } from '$lib/server/db/schema';
import { and, eq, inArray, isNull, ne, notInArray, or } from 'drizzle-orm';
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

    const todayISO = new Date().toISOString().slice(0, 10);
    const dateCol = type === 'morning'
        ? participantContacts.morningReminderDate
        : participantContacts.afternoonReminderDate;

    // Find participant IDs that already have a session for this slot
    const completedSessions = await db
        .select({ participantId: sessions.participantId })
        .from(sessions)
        .where(eq(sessions.slot, slot));

    const completedIds = completedSessions.map(s => s.participantId);

    // Get contacts who have reminders enabled, haven't been reminded today, and haven't started yet
    // Participants 1 and 17 always get reminders regardless of preference (work email auto-unsubscribes)
    const remindersOverride = [1, 17];
    const notRemindedToday = or(isNull(dateCol), ne(dateCol, todayISO));
    const baseCondition = and(
        or(eq(participantContacts.emailReminders, true), inArray(participantContacts.participantId, remindersOverride)),
        notRemindedToday
    );
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
        return json({ sent: 0, reason: 'No pending participants to remind' });

    const subject = type === 'morning'
        ? 'Reminder: today is a session day'
        : 'Last reminder: complete your session today';

    let sent = 0;
    const failures = [];

    for (const c of withEmail)
    {
        try
        {
            await sendEmail({
                to: c.email,
                subject,
                html: reminderEmail(c.name, c.code, type, c.participantId)
            });

            await db
                .update(participantContacts)
                .set(type === 'morning'
                    ? { morningReminderDate: todayISO }
                    : { afternoonReminderDate: todayISO })
                .where(eq(participantContacts.participantId, c.participantId));

            sent++;
        }
        catch (e)
        {
            failures.push(e.message);
            console.error(`Failed to send reminder to participant ${c.participantId}:`, e.message);
        }
    }

    return json({ sent, failed: failures.length, failures });
}
