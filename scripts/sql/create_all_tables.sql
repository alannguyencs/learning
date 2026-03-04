-- Learning App - Database Schema
-- Tables:
--   1. users - User authentication
--   2. quiz_questions - Pre-generated question bank
--   3. quiz_logs - Per quiz served to a user
--   4. user_topic_memory - MEMORIZE state per topic
--   5. user_lesson_memory - MEMORIZE state per lesson

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role VARCHAR
);

CREATE TABLE quiz_questions (
    id SERIAL PRIMARY KEY,
    topic_id VARCHAR NOT NULL,
    lesson_id INTEGER NOT NULL,
    lesson_filename VARCHAR NOT NULL,
    topic_name VARCHAR,
    lesson_name VARCHAR,
    quiz_type VARCHAR NOT NULL,
    question TEXT NOT NULL,
    quiz_learnt TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_options JSONB NOT NULL,
    response_to_user_option_a TEXT NOT NULL,
    response_to_user_option_b TEXT NOT NULL,
    response_to_user_option_c TEXT NOT NULL,
    response_to_user_option_d TEXT NOT NULL,
    quiz_take_away TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_qq_topic_lesson_type ON quiz_questions(topic_id, lesson_id, quiz_type);
CREATE INDEX idx_qq_lesson_type ON quiz_questions(lesson_id, quiz_type);

CREATE TABLE quiz_logs (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL REFERENCES users(username),
    quiz_question_id INTEGER NOT NULL REFERENCES quiz_questions(id),
    topic_id VARCHAR NOT NULL,
    lesson_id INTEGER NOT NULL,
    quiz_type VARCHAR NOT NULL,
    user_answer JSONB,
    assessment_result VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_ql_user_topic ON quiz_logs(username, topic_id);
CREATE INDEX idx_ql_user_lesson ON quiz_logs(username, lesson_id);
CREATE INDEX idx_ql_user_created ON quiz_logs(username, created_at);

CREATE TABLE user_topic_memory (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL REFERENCES users(username),
    topic_id VARCHAR NOT NULL,
    forgetting_rate FLOAT NOT NULL CHECK (forgetting_rate > 0),
    last_review_at TIMESTAMP,
    last_review_quiz_count INTEGER NOT NULL DEFAULT 0,
    review_count INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    UNIQUE(username, topic_id)
);

CREATE TABLE user_lesson_memory (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL REFERENCES users(username),
    topic_id VARCHAR NOT NULL,
    lesson_id INTEGER NOT NULL,
    forgetting_rate FLOAT NOT NULL CHECK (forgetting_rate > 0),
    last_review_at TIMESTAMP,
    last_review_quiz_count INTEGER NOT NULL DEFAULT 0,
    review_count INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    UNIQUE(username, lesson_id)
);
CREATE INDEX idx_ulm_user_topic ON user_lesson_memory(username, topic_id);
