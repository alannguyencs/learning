-- Add lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    topic VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    published_date DATE,
    content TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lessons_topic ON lessons(topic);

-- Seed from existing quiz_questions data
INSERT INTO lessons (id, topic, title, published_date, content)
SELECT DISTINCT ON (qq.lesson_id)
    qq.lesson_id,
    qq.topic_id,
    COALESCE(qq.lesson_name, 'Lesson ' || qq.lesson_id),
    NULL,
    NULL
FROM quiz_questions qq
ORDER BY qq.lesson_id, qq.id
ON CONFLICT (id) DO NOTHING;

-- Reset sequence to max existing ID
SELECT setval('lessons_id_seq', COALESCE((SELECT MAX(id) FROM lessons), 0) + 1, false);

-- Add FK from quiz_questions to lessons
ALTER TABLE quiz_questions
    ADD CONSTRAINT fk_qq_lesson_id FOREIGN KEY (lesson_id) REFERENCES lessons(id);
