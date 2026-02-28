import { fail, redirect } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { participants } from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';

export const actions = 
{
    default: async ({ request, cookies }) => 
    {
        const data = await request.formData();
        const code = data.get('code');
        
        const [participant] = await db.select().from(participants).where(eq(participants.code, code));
        
        if (!participant)
            return fail(400, { error: 'Invalid code' });
            
        cookies.set('participantId', String(participant.id),
        {
            path: '/',
            httpOnly: true,
            maxAge: 2629743 // 1 month
        });
        
        redirect(303, '/');
    }
}