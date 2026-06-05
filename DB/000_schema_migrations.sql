-- Migration: 000_schema_migrations.sql
-- Description: Create a table to track applied schema migrations.

CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('000_schema_migrations.sql') ON CONFLICT DO NOTHING;
