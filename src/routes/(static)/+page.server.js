import { redirect } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { sessions } from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';

export async function load({ url, locals })
{
    const [existing] = await db.select({ id: sessions.id }).from(sessions).where(eq(sessions.participantId, locals.participantId)).limit(1);

    return {
        reason: url.searchParams.get('reason'),
        next: url.searchParams.get('next'),
        isFirstSession: !existing
    };
}

export const actions = 
{
    logout: async ({ cookies }) => 
    {
        cookies.delete('participantId', { path: '/' });
        redirect(303, '/login');
    }
}