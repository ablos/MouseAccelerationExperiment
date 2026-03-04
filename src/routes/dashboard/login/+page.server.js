import { fail, redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export const actions = 
{
    default: async ({ request, cookies }) => 
    {
        const data = await request.formData();
        const password = data.get('password');
        
        if (password !== env.DASHBOARD_PASSWORD)
            return fail(400, { error: 'Wrong password' });
            
        cookies.set('researcherAuth', password, 
        {
            path: '/dashboard',
            httpOnly: true,
            maxAge: 2592000
        });
        
        redirect(303, '/dashboard');
    }
}