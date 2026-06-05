-- Migration: 008_create_channel_permissions.sql
-- Description: Create permissions and role_permissions tables.

-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id BIGSERIAL PRIMARY KEY,
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    permission_key VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- Create role_permissions table
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id BIGINT REFERENCES roles(id) ON DELETE CASCADE,
    permission_id BIGINT REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('008_create_channel_permissions.sql') ON CONFLICT DO NOTHING;
