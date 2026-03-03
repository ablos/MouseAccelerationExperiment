export function addDays(isoString, days)
{
    const [year, month, day] = isoString.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    d.setDate(d.getDate() + days);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

// config: { startDate, endDate, dayInterval, gracePeriod }
export function generateSlots(config)
{
    if (!config?.startDate || !config?.endDate || !config?.dayInterval) return [];

    const { startDate, endDate, dayInterval, gracePeriod = 0 } = config;
    const slots = [];
    let currentDate = startDate;
    let slotIndex = 1;

    while (currentDate <= endDate)
    {
        let end = addDays(currentDate, gracePeriod);
        if (end > endDate) end = endDate;

        slots.push({ slotIndex, start: currentDate, end });

        currentDate = addDays(currentDate, dayInterval);
        slotIndex++;
    }

    return slots;
}

export function formatDate(isoString)
{
    if (!isoString) return 'Unknown';
    const [year, month, day] = isoString.split('-').map(Number);
    return new Intl.DateTimeFormat('en-US',
    {
        weekday: 'long',
        month: 'long',
        day: 'numeric'
    }).format(new Date(year, month - 1, day));
}
