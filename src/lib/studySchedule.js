export function getCurrentSlot(studyConfig, today = new Date()) 
{
    const { startDate, endDate, dayInterval, gracePeriod } = studyConfig;
    if (!startDate || !endDate || !dayInterval || gracePeriod == 0) return null;
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // Strip time component
    const todayUTC = new Date(today.toISOString().slice(0, 10));
    
    // Before experiment start
    const offset = Math.round((todayUTC - start) / 86400000)
    if (offset < 0) return null;
    
    // Between slots
    if (offset % dayInterval > gracePeriod) return null;
    
    const slot = Math.floor(offset / dayInterval) + 1;
    
    // After experiment end
    const primaryDate = new Date(start);
    primaryDate.setUTCDate(primaryDate.getUTCDate() + (slot - 1) * dayInterval);
    if (primaryDate > end) return null;
    
    return slot;
}

export function getNextSlotDate(studyConfig, today = new Date()) 
{
    const { startDate, endDate, dayInterval, gracePeriod } = studyConfig;
    if (!startDate || !endDate || !dayInterval || gracePeriod == 0) return null;
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    const todayUTC = new Date(today.toISOString().slice(0, 10));
    
    const offset = Math.round((todayUTC - start) / 86400000);
    
    if (offset < 0) return start;
    
    const nextSlotIndex = Math.floor(offset / dayInterval) + 1;
    const nextDate = new Date(start);
    nextDate.setUTCDate(nextDate.getUTCDate() + nextSlotIndex * dayInterval);
    
    return nextDate > end ? null : nextDate;
}