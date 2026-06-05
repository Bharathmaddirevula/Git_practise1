-- Migration: 004_create_super_admin_permissions.sql
-- Description: Create super_admin_permissions and super_admin_role_permissions tables and seed defaults.

-- Create super_admin_permissions table
CREATE TABLE IF NOT EXISTS super_admin_permissions (
    id BIGSERIAL PRIMARY KEY,
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    permission_key VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- Create super_admin_role_permissions table
CREATE TABLE IF NOT EXISTS super_admin_role_permissions (
    role_id BIGINT REFERENCES super_admin_roles(id) ON DELETE CASCADE,
    permission_id BIGINT REFERENCES super_admin_permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- Seed Default Super Admin Permissions
INSERT INTO super_admin_permissions (permission_name, permission_key, description) VALUES
('Database Management', 'DATABASE_MANAGEMENT', 'Manage databases and run migrations'),
('Platform Management', 'PLATFORM_MANAGEMENT', 'Manage global platform configuration'),
('Logs Management', 'LOGS_MANAGEMENT', 'View and export system logs'),
('Channel Management', 'CHANNEL_MANAGEMENT', 'Manage tenant channels'),
('Channel Limit Management', 'CHANNEL_LIMIT_MANAGEMENT', 'Modify limits and quotas for tenant channels'),
('Channel Role Management', 'CHANNEL_ROLE_MANAGEMENT', 'Configure permissions and default roles for tenants'),
('User Management', 'USER_MANAGEMENT', 'Manage platform users and super admins'),
('Feature Flag Management', 'FEATURE_FLAG_MANAGEMENT', 'Manage platform-wide feature flags'),
('Audit Log Management', 'AUDIT_LOG_MANAGEMENT', 'Read and filter platform-wide audit logs')
ON CONFLICT (permission_key) DO NOTHING;

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('004_create_super_admin_permissions.sql') ON CONFLICT DO NOTHING;
