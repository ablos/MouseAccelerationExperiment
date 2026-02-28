import { redirect } from '@sveltejs/kit';

export const actions = 
{
    logout: async ({ cookies }) => 
    {
        cookies.delete('participantId', { path: '/' });
        redirect(303, '/login');
    }
}