export class MouseCoordinate
{
    constructor(x, y, trialStartTime) 
    {
        this.x = x;
        this.y = y;
        this.timeStamp = Date.now() - trialStartTime;
    }
}

export class Trial 
{
    constructor(startX, startY, targetX, targetY, targetSize) 
    {
        this.startX = startX;           // Cursor start position
        this.startY = startY;
        this.endX = null;               // Cursor end position
        this.endY = null;
        this.targetX = targetX;         // Target position
        this.targetY = targetY;
        this.targetSize = targetSize;
        this.startTime = Date.now();
        this.endTime = null;
        this.coordinates = [];
    }
    
    addCoordinate(mouseCoordinate) 
    {
        this.coordinates.push(mouseCoordinate);
    }
    
    complete(endX, endY) 
    {
        this.endX = endX;
        this.endY = endY;
        this.endTime = Date.now();
    }
}

export class Task 
{
    constructor(taskType) 
    {
        this.taskType = taskType;
        this.sessionId = null;
        this.startTime = Date.now();
        this.endTime = null;
        this.trials = [];
    }
    
    addTrial(trial) 
    {
        this.trials.push(trial);
    }
    
    complete() 
    {
        this.endTime = Date.now();
    }
}

export class Session 
{
    constructor(participantId, screenResX, screenResY, pxPerMm) 
    {
        this.participantId = participantId,
        this.screenResX = screenResX,
        this.screenResY = screenResY,
        this.pxPerMm = pxPerMm
    }
}