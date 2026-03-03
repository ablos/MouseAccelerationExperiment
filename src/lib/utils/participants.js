export function getParticipantStatus(participant, sessionCount, totalSlots = 7)
{
    if (sessionCount === 0) return 'Invited';
    if (sessionCount >= totalSlots) return 'Complete';
    if (!participant.group) return 'Needs Assignment';
    return 'Active';
}
