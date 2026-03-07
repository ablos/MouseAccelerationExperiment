// config: { startDate, endDate }
export function generateSlots(config)
{
    if (!config?.startDate || !config?.endDate) return [];

    const { startDate, endDate } = config;
    const slots = [];
    const [sy, sm, sd] = startDate.split('-').map(Number);
    const [ey, em, ed] = endDate.split('-').map(Number);
    let d = new Date(Date.UTC(sy, sm - 1, sd));
    const end = new Date(Date.UTC(ey, em - 1, ed));
    let slotIndex = 1;

    while (d <= end)
    {
        const dow = d.getUTCDay();
        if (dow !== 0 && dow !== 6)
        {
            const iso = `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}-${String(d.getUTCDate()).padStart(2, '0')}`;
            slots.push({ slotIndex, start: iso, end: iso });
            slotIndex++;
        }
        d.setUTCDate(d.getUTCDate() + 1);
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
