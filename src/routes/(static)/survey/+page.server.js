import { fail, redirect } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { participants } from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';

export const actions = 
{
    default: async ({ request, locals }) => 
    {
        const data = await request.formData();
        const age = Number(data.get('age'));
        
        await db.update(participants).set({ age }).where(eq(participants.id, locals.participantId));
        
        redirect(303, '/session');
    }
}