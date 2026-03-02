import postgres from 'postgres';
import { drizzle } from 'drizzle-orm/postgres-js';
import { mouseCoordinates, trials, tasks, sessions, participantContacts, participants } from './schema.js';

const client = postgres(process.env.DATABASE_URL);
const db = drizzle(client);

async function reset() {
    console.log('Resetting database...');
    await db.delete(mouseCoordinates);
    await db.delete(trials);
    await db.delete(tasks);
    await db.delete(sessions);
    await db.delete(participantContacts);
    await db.delete(participants);
    console.log('Done.');
    await client.end();
}

reset().catch(e => { console.error(e); process.exit(1); });
