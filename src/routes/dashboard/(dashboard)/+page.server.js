import { redirect } from '@sveltejs/kit';

export const actions = 
{
    logout: async ({ cookies }) => 
    {
        cookies.delete('researcherAuth', { path: '/dashboard' });
        redirect(303, '/dashboard/login');
    }
}