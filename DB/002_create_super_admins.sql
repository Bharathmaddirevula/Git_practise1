-- Migration: 002_create_super_admins.sql
-- Description: Create the super_admins table and update trigger function.

-- Common trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create super_admins table
CREATE TABLE IF NOT EXISTS super_admins (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'ACTIVE' NOT NULL,
    last_login TIMESTAMPTZ,
    two_factor_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    two_factor_secret VARCHAR(100),
    phone VARCHAR(20),
    total_users INT DEFAULT 0 NOT NULL,
    active_users INT DEFAULT 0 NOT NULL,
    logged_in_users INT DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Trigger to automatically update updated_at
CREATE TRIGGER trigger_update_super_admins_updated_at
    BEFORE UPDATE ON super_admins
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Indexes for performance and searchability
CREATE INDEX idx_super_admins_email ON super_admins(email);
CREATE INDEX idx_super_admins_uuid ON super_admins(uuid);
CREATE INDEX idx_super_admins_status ON super_admins(status);

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('002_create_super_admins.sql') ON CONFLICT DO NOTHING;
