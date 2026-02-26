import { db } from "$lib/server/db";
import { json } from "@sveltejs/kit";
import { eq } from "drizzle-orm";
import { sessions } from "$lib/server/db/schema";

export async function PATCH({ params }) 
{
    const id = parseInt(params.id);
    
    await db.update(sessions)
        .set({ endTime: new Date(Date.now()) })
        .where(eq(sessions.id, id));
    
    return json({ ok: true });
}