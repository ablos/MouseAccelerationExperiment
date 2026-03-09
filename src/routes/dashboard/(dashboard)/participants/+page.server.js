import { db } from '$lib/server/db';
import { participants, participantContacts, sessions, tasks, trials, mouseCoordinates, studyConfig } from '$lib/server/db/schema';
import { eq, and, inArray, isNull } from 'drizzle-orm';
import { fail } from '@sveltejs/kit';
import { sendEmail } from '$lib/server/mailer.js';
import { invitationEmail } from '$lib/server/emails/invitation.js';
import { getSessionMetrics } from '$lib/utils/metrics.js';

export async function load() 
{
    const allParticipants = await db.select().from(participants);
    const allSessions = await db.select({ participantId: sessions.participantId }).from(sessions);
    const [config] = await db.select().from(studyConfig);
    
    return { participants: allParticipants, sessions: allSessions, config };
}

export const actions = {
    createParticipant: async ({ request }) => {
        const data = await request.formData();
        const name = data.get('name')?.toString().trim() || null;
        const email = data.get('email')?.toString().trim() || null;
        const phone = data.get('phone')?.toString().trim() || null;
        const notes = data.get('notes')?.toString().trim() || null;
        
        // Check if email already exists
        const existingContact = await db.select({ participantId: participantContacts.participantId }).from(participantContacts).where(eq(participantContacts.email, email));
        
        if (existingContact.length) 
        {
            const [existingParticipant] = await db.select({ id: participants.id, code: participants.code }).from(participants).where(eq(participants.id, existingContact[0].participantId));
            
            return fail(400, 
            {
                error: 'Email already registered.',
                participantId: existingParticipant.id,
                code: existingParticipant.code
            });
        }
        
        let code;
        for (let i = 0; i < 20; i++) 
        {
            const candidate = Math.floor(10000 + Math.random() * 90000);
            const existingCode = await db.select({ id: participants.id }).from(participants).where(eq(participants.code, candidate));
            
            if (!existingCode.length) 
            {
                code = candidate;
                break;
            }
        }
        
        if (!code) return fail(500, { error: 'Could not generate unique code, try again.' });
        
        const [participant] = await db.insert(participants).values({ code }).returning();
        
        if (name || email || phone || notes) 
        {
            await db.insert(participantContacts).values(
            {
                participantId: participant.id,
                name,
                email,
                phone,
                notes
            });
        }
        
        await sendEmail({
            to: email,
            subject: 'You have been invited to participate in a study',
            html: invitationEmail(name, code)
        });
        
        return { code };
    },

    assignGroup: async ({ request }) => {
        const data = await request.formData();
        const participantId = parseInt(data.get('participantId'));
        const group = data.get('group')?.toString();

        if (!participantId || !['control', 'experimental'].includes(group))
            return fail(400, { assignError: 'Invalid data' });

        await db.update(participants).set({ group }).where(eq(participants.id, participantId));
        return { assigned: true };
    },

    autoAssign: async () => {
        const unassigned = await db.select().from(participants).where(isNull(participants.group));
        if (!unassigned.length) return { autoAssigned: 0 };

        const pIds = unassigned.map(p => p.id);
        const baselineSessions = await db.select().from(sessions)
            .where(and(inArray(sessions.participantId, pIds), eq(sessions.slot, 1)));

        if (!baselineSessions.length) return { autoAssigned: 0 };

        const sIds = baselineSessions.map(s => s.id);
        const allTasks = await db.select().from(tasks).where(inArray(tasks.sessionId, sIds));
        const tIds = allTasks.map(t => t.id);
        const allTrials = tIds.length ? await db.select().from(trials).where(inArray(trials.taskId, tIds)) : [];
        const trialIds = allTrials.map(t => t.id);
        const allCoords = trialIds.length ? await db.select().from(mouseCoordinates).where(inArray(mouseCoordinates.trialId, trialIds)) : [];

        // Compute all 4 metrics from baseline for each participant
        const metricsList = [];
        for (const session of baselineSessions) {
            const participant = unassigned.find(p => p.id === session.participantId);
            const metrics = getSessionMetrics(session, allTasks, allTrials, allCoords);
            const { time, accuracy, plr, submovements } = metrics.combined;
            if (time === null || accuracy === null) continue;
            metricsList.push({ participant, time, accuracy, plr, submovements });
        }

        if (!metricsList.length) return { autoAssigned: 0 };

        // Rank each participant per metric (1 = best), average ranks for composite score
        function rankBy(key, higherIsBetter = false) {
            const sorted = [...metricsList].sort((a, b) => higherIsBetter ? b[key] - a[key] : a[key] - b[key]);
            sorted.forEach((item, i) => item[`rank_${key}`] = i + 1);
        }

        rankBy('time');
        rankBy('accuracy');
        rankBy('plr');
        rankBy('submovements');

        const scored = metricsList.map(item => {
            const metrics = ['time', 'accuracy', 'plr', 'submovements'].filter(k => item[k] !== null);
            const avgRank = metrics.reduce((sum, k) => sum + item[`rank_${k}`], 0) / metrics.length;
            return { participant: item.participant, score: avgRank };
        });

        // Sort ascending (lower avg rank = better performance)
        scored.sort((a, b) => a.score - b.score);

        // Split into thirds, randomly assign within each subgroup
        const n = scored.length;
        const assignments = [];

        for (let i = 0; i < 3; i++) {
            const subgroup = scored.slice(Math.floor(i * n / 3), Math.floor((i + 1) * n / 3));

            // Fisher-Yates shuffle
            for (let j = subgroup.length - 1; j > 0; j--) {
                const k = Math.floor(Math.random() * (j + 1));
                [subgroup[j], subgroup[k]] = [subgroup[k], subgroup[j]];
            }

            const half = Math.ceil(subgroup.length / 2);
            subgroup.forEach((item, idx) => {
                assignments.push({ id: item.participant.id, group: idx < half ? 'control' : 'experimental' });
            });
        }

        for (const { id, group } of assignments)
            await db.update(participants).set({ group }).where(eq(participants.id, id));

        return { autoAssigned: assignments.length };
    }
};