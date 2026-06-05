-- Migration: 001_create_extensions.sql
-- Description: Enable required PostgreSQL extensions.

-- Enable uuid-ossp for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for password hashing or cryptographic functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('001_create_extensions.sql') ON CONFLICT DO NOTHING;
