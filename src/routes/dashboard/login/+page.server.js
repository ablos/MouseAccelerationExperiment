import { fail, redirect } from '@sveltejs/kit';
import { DASHBOARD_PASSWORD } from '$env/static/private';

export const actions = 
{
    default: async ({ request, cookies }) => 
    {
        const data = await request.formData();
        const password = data.get('password');
        
        if (password !== DASHBOARD_PASSWORD)
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