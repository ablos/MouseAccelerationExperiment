import { redirect } from '@sveltejs/kit';

export async function load({ url }) 
{
    return {
        reason: url.searchParams.get('reason'),
        next: url.searchParams.get('next')
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