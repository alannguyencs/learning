-- Prepare cloud database for a full restore from local dump.
-- Drops tables in correct order to satisfy foreign keys.
-- Run this manually before restore if you want a clean cloud DB,
-- or use --no-clean with the Python upload script.
--
-- Usage (after loading .env):
--   PGPASSWORD=$CLOUD_DB_PASSWORD psql -h $CLOUD_DB_URL -U $CLOUD_DB_USERNAME \
--     -d $CLOUD_DB_NAME -f scripts/sql/prepare_cloud_for_upload.sql

BEGIN;

-- Drop tables that reference users or quiz_questions first
DROP TABLE IF EXISTS quiz_logs CASCADE;
DROP TABLE IF EXISTS user_lesson_memory CASCADE;
DROP TABLE IF EXISTS user_topic_memory CASCADE;

-- Drop independent tables
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS quiz_questions CASCADE;

COMMIT;
