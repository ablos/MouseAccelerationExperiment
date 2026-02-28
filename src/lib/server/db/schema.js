import { pgTable, serial, integer, text, timestamp, real, bigint } from 'drizzle-orm/pg-core';

export const participants = pgTable('participants', {
	id: serial('id').primaryKey(),
	code: text('code').notNull().unique(),
	group: text('group'),
	age: integer('age')
});

export const sessions = pgTable('sessions', {
	id: serial('id').primaryKey(),
	participantId: integer('participant_id')
		.notNull()
		.references(() => participants.id),
	startTime: timestamp('start_time').notNull(),
	endTime: timestamp('end_time'),
	screenResX: integer('screen_res_x').notNull(),
	screenResY: integer('screen_res_y').notNull(),
	screenPxPerMm: real('screen_px_per_mm').notNull()
});

export const tasks = pgTable('tasks', {
	id: serial('id').primaryKey(),
	taskType: text('task_type').notNull(),
	sessionId: integer('session_id')
		.notNull()
		.references(() => sessions.id),
	startTime: timestamp('start_time').notNull(),
	endTime: timestamp('end_time')
});

export const trials = pgTable('trials', {
	id: serial('id').primaryKey(),
	taskId: integer('task_id')
		.notNull()
		.references(() => tasks.id),
	startTime: timestamp('start_time').notNull(),
	endTime: timestamp('end_time'),
	startX: real('start_x').notNull(),
	startY: real('start_y').notNull(),
	endX: real('end_x'),
	endY: real('end_y'),
	targetX: real('target_x').notNull(),
	targetY: real('target_y').notNull(),
	targetSize: real('target_size').notNull()
});

// timestamp is stored as ms elapsed since trial start (not an absolute time)
export const mouseCoordinates = pgTable('mouse_coordinates', {
	id: serial('id').primaryKey(),
	trialId: integer('trial_id')
		.notNull()
		.references(() => trials.id),
	timestamp: bigint('timestamp', { mode: 'number' }).notNull(),
	x: real('x').notNull(),
	y: real('y').notNull()
});
