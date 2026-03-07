function getWorkdays(startDate, endDate)
{
    const days = [];
    const [sy, sm, sd] = startDate.split('-').map(Number);
    const [ey, em, ed] = endDate.split('-').map(Number);
    let d = new Date(Date.UTC(sy, sm - 1, sd));
    const end = new Date(Date.UTC(ey, em - 1, ed));

    while (d <= end)
    {
        const dow = d.getUTCDay(); // 0=Sun, 6=Sat
        if (dow !== 0 && dow !== 6)
        {
            const y = d.getUTCFullYear();
            const m = String(d.getUTCMonth() + 1).padStart(2, '0');
            const day = String(d.getUTCDate()).padStart(2, '0');
            days.push(`${y}-${m}-${day}`);
        }
        d.setUTCDate(d.getUTCDate() + 1);
    }
    return days;
}

export function getCurrentSlot(studyConfig, today = new Date())
{
    const { startDate, endDate } = studyConfig;
    if (!startDate || !endDate) return null;

    const todayISO = today.toISOString().slice(0, 10);
    const workdays = getWorkdays(startDate, endDate);
    const idx = workdays.indexOf(todayISO);
    return idx === -1 ? null : idx + 1;
}

export function getNextSlotDate(studyConfig, today = new Date())
{
    const { startDate, endDate } = studyConfig;
    if (!startDate || !endDate) return null;

    const todayISO = today.toISOString().slice(0, 10);
    const workdays = getWorkdays(startDate, endDate);
    const next = workdays.find(d => d > todayISO);
    if (!next) return null;

    const [y, m, d] = next.split('-').map(Number);
    return new Date(Date.UTC(y, m - 1, d));
}