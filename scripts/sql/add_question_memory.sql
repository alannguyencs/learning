CREATE TABLE IF NOT EXISTS user_question_memory (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL REFERENCES users(username),
    quiz_question_id INTEGER NOT NULL REFERENCES quiz_questions(id),
    forgetting_rate FLOAT NOT NULL DEFAULT 0.3,
    last_review_at TIMESTAMP,
    last_review_quiz_count INTEGER NOT NULL DEFAULT 0,
    review_count INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_question_forgetting_rate_positive CHECK (forgetting_rate > 0),
    CONSTRAINT uq_user_question_memory UNIQUE (username, quiz_question_id)
);

CREATE INDEX IF NOT EXISTS idx_question_memory_user
    ON user_question_memory (username);
