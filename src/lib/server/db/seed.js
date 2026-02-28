import postgres from 'postgres';
import { drizzle } from 'drizzle-orm/postgres-js';
import { participants, sessions } from './schema.js';

const client = postgres(process.env.DATABASE_URL);
const db = drizzle(client);

const participantData = [
    { code: 'P001', group: 'control',      age: 22, gender: 'male',   handedness: 'right', hoursPerWeek: 10, gamingExperience: 'casual' },
    { code: 'P002', group: 'experimental', age: 25, gender: 'female',  handedness: 'right', hoursPerWeek: 20, gamingExperience: 'intermediate' },
    { code: 'P003', group: null,            age: null, gender: null,   handedness: null,    hoursPerWeek: null, gamingExperience: null },
    { code: 'P004', group: 'control',      age: 19, gender: 'male',   handedness: 'left',  hoursPerWeek: 5,  gamingExperience: 'none' },
    { code: 'P005', group: 'experimental', age: 28, gender: 'female',  handedness: 'right', hoursPerWeek: 35, gamingExperience: 'hardcore' },
    { code: 'P006', group: null,            age: 23, gender: 'male',   handedness: 'right', hoursPerWeek: 8,  gamingExperience: 'casual' },
    { code: 'P007', group: null,            age: null, gender: null,   handedness: null,    hoursPerWeek: null, gamingExperience: null },
    { code: 'P008', group: 'control',      age: 21, gender: 'female',  handedness: 'right', hoursPerWeek: 15, gamingExperience: 'intermediate' },
    { code: 'P009', group: 'experimental', age: 24, gender: 'male',   handedness: 'right', hoursPerWeek: 12, gamingExperience: 'casual' },
    { code: 'P010', group: null,            age: 26, gender: 'female',  handedness: 'left',  hoursPerWeek: 3,  gamingExperience: 'none' },
    { code: 'P011', group: null,            age: null, gender: null,   handedness: null,    hoursPerWeek: null, gamingExperience: null },
    { code: 'P012', group: 'experimental', age: 20, gender: 'other',   handedness: 'right', hoursPerWeek: 25, gamingExperience: 'hardcore' },
];

// sessions per participant code: 0 = Invited, 1-2 = Needs Assignment (no group), 1-6 = Active, 7+ = Complete
const sessionCounts = {
    P001: 3, P002: 5, P003: 0, P004: 2,
    P005: 7, P006: 2, P007: 0, P008: 8,
    P009: 4, P010: 1, P011: 0, P012: 1,
};

function makeSession(participantId, offsetDays) {
    const start = new Date(Date.now() - offsetDays * 86_400_000);
    const end = new Date(start.getTime() + 45 * 60 * 1000); // 45 min session
    return {
        participantId,
        startTime: start,
        endTime: end,
        screenResX: 1920,
        screenResY: 1080,
        screenPxPerMm: 4.47,
    };
}

async function seed() {
    console.log('Seeding participants...');
    const inserted = await db.insert(participants).values(participantData).returning();

    const byCode = Object.fromEntries(inserted.map(p => [p.code, p]));

    const allSessions = [];
    for (const [code, count] of Object.entries(sessionCounts)) {
        const p = byCode[code];
        for (let i = 0; i < count; i++) {
            allSessions.push(makeSession(p.id, (count - i) * 3));
        }
    }

    if (allSessions.length) {
        console.log(`Seeding ${allSessions.length} sessions...`);
        await db.insert(sessions).values(allSessions);
    }

    console.log('Done.');
    await client.end();
}

seed().catch(e => { console.error(e); process.exit(1); });
