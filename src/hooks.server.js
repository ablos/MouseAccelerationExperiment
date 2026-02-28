import { db } from '$lib/server/db';
import { participants } from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';
import { DASHBOARD_PASSWORD } from '$env/static/private';

export async function handle({ event, resolve }) 
{
    const isDashboard = event.url.pathname.startsWith('/dashboard');
    
    if (isDashboard) 
    {
        const auth = event.cookies.get('researcherAuth');
        
        if ((!auth || auth !== DASHBOARD_PASSWORD) && event.url.pathname !== '/dashboard/login')
            return Response.redirect(new URL('/dashboard/login', event.url), 303);
            
        return resolve(event);
    }

    const participantId = event.cookies.get('participantId');
    
    if (participantId)
        event.locals.participantId = Number(participantId);
        
    // Redirect unauthenticated users to /login
    if (!participantId && event.url.pathname !== '/login')
        return Response.redirect(new URL('/login', event.url), 303);
        
    // Redirect already authenticated users away from /login
    if (participantId && event.url.pathname === '/login')
        return Response.redirect(new URL('/', event.url), 303);
        
    // Redirect participant to survey if it has not been completed
    if (participantId && event.url.pathname === '/session') 
    {
        const [participant] = await db.select().from(participants).where(eq(participants.id, Number(participantId)));
        
        if (!participant.age)
            return Response.redirect(new URL('/survey', event.url), 303);
    }
    
    // Redirect user away from survey if already completed
    if (participantId && event.url.pathname === '/survey') 
    {
        const [participant] = await db.select().from(participants).where(eq(participants.id, Number(participantId)));

        if (participant.age)
            return Response.redirect(new URL('/', event.url), 303);
    }
        
    return resolve(event);
}