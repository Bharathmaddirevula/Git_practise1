-- Migration: 003_create_super_admin_roles.sql
-- Description: Create the super_admin_roles and super_admin_user_roles tables.

-- Create super_admin_roles table
CREATE TABLE IF NOT EXISTS super_admin_roles (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    role_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_by BIGINT REFERENCES super_admins(id) ON DELETE SET NULL,
    updated_by BIGINT REFERENCES super_admins(id) ON DELETE SET NULL,
    deleted_by BIGINT REFERENCES super_admins(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMPTZ
);

-- Trigger to automatically update updated_at for super_admin_roles
CREATE TRIGGER trigger_update_super_admin_roles_updated_at
    BEFORE UPDATE ON super_admin_roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create super_admin_user_roles table to link super admins to roles
CREATE TABLE IF NOT EXISTS super_admin_user_roles (
    super_admin_id BIGINT REFERENCES super_admins(id) ON DELETE CASCADE,
    role_id BIGINT REFERENCES super_admin_roles(id) ON DELETE CASCADE,
    PRIMARY KEY (super_admin_id, role_id)
);

-- Indexes for search and relationships
CREATE INDEX idx_super_admin_roles_uuid ON super_admin_roles(uuid);

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('003_create_super_admin_roles.sql') ON CONFLICT DO NOTHING;
