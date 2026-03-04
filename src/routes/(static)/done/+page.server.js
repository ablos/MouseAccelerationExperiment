import { db } from "$lib/server/db";
import { studyConfig } from "$lib/server/db/schema";
import { getNextSlotDate } from "$lib/studySchedule";

export async function load() 
{
    const [config] = await db.select().from(studyConfig);
    const nextSlotDate = config ? getNextSlotDate(config) : null;
    
    return {
        nextSlotDate: nextSlotDate?.toISOString() ?? null
    }
}