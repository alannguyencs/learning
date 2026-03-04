-- Migration: add topic_name and lesson_name to quiz_questions
-- These columns allow the server to auto-register topics from uploaded questions.

ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS topic_name VARCHAR;
ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS lesson_name VARCHAR;

-- Backfill existing data from known mappings
UPDATE quiz_questions SET topic_name = 'Sample Topic' WHERE topic_id = 'sample_topic' AND topic_name IS NULL;
UPDATE quiz_questions SET topic_name = 'The MIT Monk' WHERE topic_id = 'theMITmonk' AND topic_name IS NULL;
UPDATE quiz_questions SET topic_name = 'Coach' WHERE topic_id = 'coach' AND topic_name IS NULL;

UPDATE quiz_questions SET lesson_name = 'Sample Lesson 1' WHERE lesson_id = 1 AND lesson_name IS NULL;
UPDATE quiz_questions SET lesson_name = 'Sample Lesson 2' WHERE lesson_id = 2 AND lesson_name IS NULL;
UPDATE quiz_questions SET lesson_name = 'The 3C Learning Protocol' WHERE lesson_id = 3 AND lesson_name IS NULL;
UPDATE quiz_questions SET lesson_name = 'Bloom: LLM-Augmented Behavior Change' WHERE lesson_id = 4 AND lesson_name IS NULL;
