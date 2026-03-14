-- Migration: add topic_name column to lessons table
ALTER TABLE lessons ADD COLUMN IF NOT EXISTS topic_name VARCHAR;

-- Backfill from quiz_questions (pick the first non-null topic_name per lesson)
UPDATE lessons l
SET topic_name = sq.topic_name
FROM (
    SELECT DISTINCT ON (lesson_id) lesson_id, topic_name
    FROM quiz_questions
    WHERE topic_name IS NOT NULL
    ORDER BY lesson_id, id
) sq
WHERE l.id = sq.lesson_id AND l.topic_name IS NULL;
