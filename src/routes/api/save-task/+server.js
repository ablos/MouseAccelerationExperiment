import { db } from "$lib/server/db";
import { participants, sessions, tasks, trials, mouseCoordinates } from "$lib/server/db/schema";
import { json } from "@sveltejs/kit";

export async function POST({ request }) 
{
    // Parse the task object
    const task = await request.json();
    
    // Insert task into db and get back generated id
    const [{ taskId }] = await db.insert(tasks).values(
        {
            taskType: task.taskType,
            sessionId: task.sessionId,
            startTime: new Date(task.startTime),
            endTime: new Date(task.endTime)
        }).returning({ taskId: tasks.id });
    
    for (const trial of task.trials) 
    {
        // Insert trial into db and get back generated id
        const [{ trialId }] = await db.insert(trials).values(
            {
                taskId,
                startTime: new Date(trial.startTime),
                endTime: new Date(trial.endTime),
                startX: trial.startX,
                startY: trial.startY,
                endX: trial.endX,
                endY: trial.endY,
                targetX: trial.targetX,
                targetY: trial.targetY,
                targetSize: trial.targetSize
            }).returning({ trialId: trials.id });
            
        // Insert mouse coordinates into db
        await db.insert(mouseCoordinates).values(
            trial.coordinates.map(c => (
                {
                    trialId,
                    timestamp: c.timeStamp,
                    x: c.x,
                    y: c.y
                }))
        );
    }
    
    return json({ ok: true });
}