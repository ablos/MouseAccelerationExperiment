export function computeTime(trials) 
{
    trials = trials.filter((t) => t.endTime);
    
    if (!trials.length) return null;

    let totalTime = trials.reduce((sum, t) => sum + t.endTime.getTime() - t.startTime.getTime(), 0);
    
    return totalTime / trials.length;
}

export function computeAccuracy(trials) 
{
    trials = trials.filter((t) => t.endX !== null && t.endY !== null);
    
    if (!trials.length) return null;
    
    let totalDistance = trials.reduce((sum, t) => sum + Math.sqrt((t.endX - t.targetX) ** 2 + (t.endY - t.targetY) ** 2), 0);
    
    return totalDistance / trials.length;
}

export function computePLR(trials, allCoords) 
{
    let totalPLR = 0;
    let validTrials = 0;

    for (const trial of trials) 
    {
        const coords = allCoords.filter(c => c.trialId === trial.id).sort((a, b) => a.timestamp - b.timestamp);
        
        if (coords.length < 2) continue;
        
        let pathLength = 0;
        
        for (let i = 1; i < coords.length; i++) 
        {
            const dx = coords[i].x - coords[i - 1].x;
            const dy = coords[i].y - coords[i - 1].y;
            
            pathLength += Math.sqrt(dx ** 2 + dy ** 2);
        }
        
        let straightLength = Math.sqrt((trial.startX - trial.targetX) ** 2 + (trial.startY - trial.targetY) ** 2);
        
        if (straightLength === 0) continue;
        
        totalPLR += pathLength / straightLength;
        validTrials++;
    }
    
    if (!validTrials) return null;
    return totalPLR / validTrials;
}

export function computeSubmovements(trials, allCoords) 
{
    let submovementCount = 0;
    let validTrials = 0;

    for (const trial of trials) 
    {
        const coords = allCoords.filter(c => c.trialId === trial.id).sort((a, b) => a.timestamp - b.timestamp);
        
        if (coords.length < 2) continue;
        
        validTrials++;
        
        let inSubmovement = false;
        let currentDir = null;
        let belowThresholdSince = null;
        let pendingDirChange = false;
        let pendingDir = null;
        let confirmDist = 0;
        
        for (let i = 1; i < coords.length; i++) 
        {
            let dt = coords[i].timestamp - coords[i - 1].timestamp;
            
            if (dt == 0) continue;
            
            let dx = coords[i].x - coords[i - 1].x;
            let dy = coords[i].y - coords[i - 1].y;
            let distance = Math.sqrt(dx ** 2 + dy ** 2);
            let velocity = distance / dt;
            let direction = Math.atan2(dy, dx);
            
            if (!inSubmovement) 
            {
                if (velocity >= 0.5) 
                {
                    inSubmovement = true;
                    submovementCount++;
                    currentDir = direction;
                    belowThresholdSince = null;
                    pendingDirChange = false;
                    confirmDist = 0;
                }
            }
            else 
            {
                // End condition 1: velocity < 0.2 for 80 ms
                if (velocity < 0.2) 
                {
                    if (belowThresholdSince === null)
                        belowThresholdSince = coords[i].timestamp;
                        
                    if (coords[i].timestamp - belowThresholdSince >= 80) 
                    {
                        inSubmovement = false;
                        belowThresholdSince = null;
                        pendingDirChange = false;
                        confirmDist = 0;
                        continue;
                    }
                }
                else 
                {
                    belowThresholdSince = null;
                }
                
                // End condition 2: direction change > 30 degree confirmed by 10px
                let angleDiff = Math.abs(direction - currentDir);
                if (angleDiff > Math.PI) angleDiff = 2 * Math.PI - angleDiff;
                
                if (pendingDirChange) 
                {
                    let diffFromPending = Math.abs(direction - pendingDir)
                    if (diffFromPending > Math.PI) diffFromPending = 2 * Math.PI - diffFromPending;
                    
                    if (diffFromPending <= Math.PI / 6) // Within 30 degrees 
                    {
                        confirmDist += distance;
                    
                        if (confirmDist >= 10) 
                        {
                            inSubmovement = false;
                            currentDir = direction;
                            belowThresholdSince = null;
                            pendingDirChange = false;
                            confirmDist = 0;
                        }
                    }
                    else 
                    {
                        pendingDirChange = false;
                        confirmDist = 0;
                        currentDir = direction;
                    }
                }
                else 
                {
                    if (angleDiff > Math.PI / 6) 
                    {
                        pendingDirChange = true;
                        pendingDir = direction;
                        confirmDist = distance;
                    }
                    else 
                    {
                        currentDir = direction;
                    }
                }
            }
        }
    }
    
    if (!validTrials) return null;
    return submovementCount / validTrials;
}

export function getSessionMetrics(session, allTasks, allTrials, allCoords) 
{
    const sessionTasks = allTasks.filter(t => t.sessionId == session.id);
    
    const clickingTask = sessionTasks.find(t => t.taskType === 'clicking');
    const clickingTrials = clickingTask ? allTrials.filter(t => t.taskId === clickingTask.id) : [];
    
    const slidingTask = sessionTasks.find(t => t.taskType === 'slider');
    const slidingTrials = slidingTask ? allTrials.filter(t => t.taskId === slidingTask.id) : [];
    
    const draggingTask = sessionTasks.find(t => t.taskType === 'dragging');
    const draggingTrials = draggingTask ? allTrials.filter(t => t.taskId === draggingTask.id) : [];
    
    const clickingTime = computeTime(clickingTrials);
    const slidingTime = computeTime(slidingTrials);
    const draggingTime = computeTime(draggingTrials);
    const times = [clickingTime, slidingTime, draggingTime].filter(t => t !== null);
    const combinedTime = times.length ? times.reduce((s, t) => s + t, 0) / times.length : null;
    
    const clickingAccuracy = computeAccuracy(clickingTrials);
    const slidingAccuracy = computeAccuracy(slidingTrials);
    const draggingAccuracy = computeAccuracy(draggingTrials);
    const accuracies = [clickingAccuracy, slidingAccuracy, draggingAccuracy].filter(t => t !== null);
    const combinedAccuracy = accuracies.length ? accuracies.reduce((s, a) => s + a, 0) / accuracies.length : null;
    
    const clickingPLR = computePLR(clickingTrials, allCoords);
    const slidingPLR = computePLR(slidingTrials, allCoords);
    const draggingPLR = computePLR(draggingTrials, allCoords);
    const plrs = [clickingPLR, slidingPLR, draggingPLR].filter(t => t !== null);
    const combinedPLR = plrs.length ? plrs.reduce((s, p) => s + p, 0) / plrs.length : null;
    
    const clickingSubs = computeSubmovements(clickingTrials, allCoords);
    const slidingSubs = computeSubmovements(slidingTrials, allCoords);
    const draggingSubs = computeSubmovements(draggingTrials, allCoords);
    const subs = [clickingSubs, slidingSubs, draggingSubs].filter(t => t !== null);
    const combinedSubs = subs.length ? subs.reduce((s, sub) => s + sub, 0) / subs.length : null;
    
    return { 
        clicking: { time: clickingTime, accuracy: clickingAccuracy, plr: clickingPLR, submovements: clickingSubs },
        sliding: { time: slidingTime, accuracy: slidingAccuracy, plr: slidingPLR, submovements: slidingSubs },
        dragging: { time: draggingTime, accuracy: draggingAccuracy, plr: draggingPLR, submovements: draggingSubs },
        combined: { time: combinedTime, accuracy: combinedAccuracy, plr: combinedPLR, submovements: combinedSubs }
    }
}