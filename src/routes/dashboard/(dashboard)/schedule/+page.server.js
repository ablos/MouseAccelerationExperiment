import { db } from "$lib/server/db";
import { studyConfig, sessions } from "$lib/server/db/schema";
import { fail } from "@sveltejs/kit";
import { eq } from "drizzle-orm";

export async function load() 
{
    const [config] = await db.select().from(studyConfig);
    
    return { config };
}

export const actions = {
    save: async ({ request }) => {
        const data = await request.formData();
        const startDate = data.get('startDate')?.toString();
        const endDate = data.get('endDate')?.toString();

        if (!startDate || !endDate)
            return fail(400, { error: 'All fields are required' });

        if (endDate <= startDate)
            return fail(400, { error: 'End date must be after start date.' });

        const [existingSession] = await db.select({ id: sessions.id }).from(sessions).limit(1);
        if (existingSession)
            return fail(400, { error: 'Cannot change config after sessions have started.' });

        const [existing] = await db.select({ id: studyConfig.id }).from(studyConfig);

        if (existing)
            await db.update(studyConfig).set({ startDate, endDate }).where(eq(studyConfig.id, existing.id));
        else
            await db.insert(studyConfig).values({ startDate, endDate });

        return { success: true };
    }    
}