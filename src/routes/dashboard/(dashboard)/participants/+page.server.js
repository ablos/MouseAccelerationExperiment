import { db } from '$lib/server/db';
import { participants, participantContacts, sessions } from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';
import { fail } from '@sveltejs/kit';
import { Resend } from 'resend';
import { RESEND_API_KEY } from '$env/static/private';
import { invitationEmail } from '$lib/server/emails/invitation.js';

const resend = new Resend(RESEND_API_KEY);

export async function load() 
{
    const allParticipants = await db.select().from(participants);
    const allSessions = await db.select({ participantId: sessions.participantId }).from(sessions);
    
    return { participants: allParticipants, sessions: allSessions };
}

export const actions = {
    createParticipant: async ({ request }) => {
        const data = await request.formData();
        const name = data.get('name')?.toString().trim() || null;
        const email = data.get('email')?.toString().trim() || null;
        const phone = data.get('phone')?.toString().trim() || null;
        const notes = data.get('notes')?.toString().trim() || null;
        
        // Check if email already exists
        const existingContact = await db.select({ participantId: participantContacts.participantId }).from(participantContacts).where(eq(participantContacts.email, email));
        
        if (existingContact.length) 
        {
            const [existingParticipant] = await db.select({ id: participants.id, code: participants.code }).from(participants).where(eq(participants.id, existingContact[0].participantId));
            
            return fail(400, 
            {
                error: 'Email already registered.',
                participantId: existingParticipant.id,
                code: existingParticipant.code
            });
        }
        
        let code;
        for (let i = 0; i < 20; i++) 
        {
            const candidate = Math.floor(10000 + Math.random() * 90000);
            const existingCode = await db.select({ id: participants.id }).from(participants).where(eq(participants.code, candidate));
            
            if (!existingCode.length) 
            {
                code = candidate;
                break;
            }
        }
        
        if (!code) return fail(500, { error: 'Could not generate unique code, try again.' });
        
        const [participant] = await db.insert(participants).values({ code }).returning();
        
        if (name || email || phone || notes) 
        {
            await db.insert(participantContacts).values(
            {
                participantId: participant.id,
                name,
                email,
                phone,
                notes
            });
        }
        
        await resend.emails.send(
        {
            from: 'Mouse Acceleration Study <mouse-study@ablos.nl>',
            to: email,
            subject: 'You have been invited to participate in a study',
            html: invitationEmail(name, code)
        });
        
        return { code };
    }
};