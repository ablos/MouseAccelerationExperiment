import { db } from '$lib/server/db';
import { participants, participantContacts } from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';

export async function GET({ url })
{
    const participantId = url.searchParams.get('id');
    const code = url.searchParams.get('code');

    if (!participantId || !code)
        return new Response('Invalid request', { status: 400 });

    const [participant] = await db
        .select({ id: participants.id, code: participants.code })
        .from(participants)
        .where(eq(participants.id, Number(participantId)));

    if (!participant || String(participant.code) !== code)
        return new Response('Invalid request', { status: 400 });

    await db
        .update(participantContacts)
        .set({ emailReminders: false })
        .where(eq(participantContacts.participantId, Number(participantId)));

    return new Response(
        '<!DOCTYPE html><html><body style="font-family:sans-serif;max-width:480px;margin:80px auto;text-align:center;">' +
        '<h2>Unsubscribed</h2>' +
        '<p>You will no longer receive session reminders. You can still participate in the study normally.</p>' +
        '</body></html>',
        { headers: { 'Content-Type': 'text/html' } }
    );
}
