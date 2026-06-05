-- Migration: 015_create_seed_data.sql
-- Description: Seed initial data for Super Admin, Permissions, Roles, Default Tenant, and Sample Channel Admin.

BEGIN;

-- 1. Create Default Super Admin Role
INSERT INTO super_admin_roles (role_name, description)
VALUES ('Super Administrator', 'Full platform administrative access')
ON CONFLICT (role_name) DO NOTHING;

-- 2. Link all default super admin permissions to Super Administrator role
INSERT INTO super_admin_role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM super_admin_roles r
CROSS JOIN super_admin_permissions p
WHERE r.role_name = 'Super Administrator'
ON CONFLICT DO NOTHING;

-- 3. Create Default Super Admin User
-- Password: SuperAdminPassword123!
INSERT INTO super_admins (username, email, password_hash, status, phone, total_users, active_users, logged_in_users)
VALUES (
    'superadmin',
    'superadmin@enterprise.com',
    crypt('SuperAdminPassword123!', gen_salt('bf', 10)),
    'ACTIVE',
    '+919999999999',
    1, -- 1 total user (channeladmin seeded below)
    1, -- 1 active user
    0  -- 0 currently logged in
)
ON CONFLICT (username) DO NOTHING;

-- 4. Assign Super Administrator role to the default Super Admin user
INSERT INTO super_admin_user_roles (super_admin_id, role_id)
SELECT u.id, r.id
FROM super_admins u
CROSS JOIN super_admin_roles r
WHERE u.username = 'superadmin' AND r.role_name = 'Super Administrator'
ON CONFLICT DO NOTHING;

-- 5. Create Default Tenant (Channel)
INSERT INTO tenants (
    tenant_name, business_name, email, phone, gst_number, pan_number, address, status, 
    domain_name, logo_url, primary_color, secondary_color, timezone, currency, support_email,
    created_by, approved_by
)
SELECT
    'Default Channel',
    'Enterprise Channel Solutions Pvt Ltd',
    'info@defaultchannel.com',
    '+919876543210',
    '29AAAAA0000A1Z5',
    'ABCDE1234F',
    '123, Business District, Tech Park, Bangalore, India',
    'ACTIVE',
    'default.enterprise.com',
    'https://cdn.enterprise.com/logos/default_tenant.png',
    '#0F172A',
    '#3B82F6',
    'Asia/Kolkata',
    'INR',
    'support@defaultchannel.com',
    u.id,
    u.id
FROM super_admins u
WHERE u.username = 'superadmin'
ON CONFLICT (email) DO NOTHING;

-- 6. Seed Tenant Limits for Default Tenant
INSERT INTO tenant_limits (tenant_id, max_users, max_storage_gb, max_api_calls, max_branches)
SELECT id, 50, 100, 1000000, 10
FROM tenants
WHERE email = 'info@defaultchannel.com'
ON CONFLICT (tenant_id) DO NOTHING;

-- 7. Seed Feature Flags for Default Tenant
INSERT INTO tenant_feature_flags (tenant_id, feature_name, enabled)
SELECT id, 'REPORTS', true FROM tenants WHERE email = 'info@defaultchannel.com' UNION ALL
SELECT id, 'NOTIFICATIONS', true FROM tenants WHERE email = 'info@defaultchannel.com' UNION ALL
SELECT id, 'API_ACCESS', true FROM tenants WHERE email = 'info@defaultchannel.com'
ON CONFLICT (tenant_id, feature_name) DO NOTHING;

-- 8. Seed Default Route Catalog for Default Tenant
INSERT INTO tenant_route_catalog (tenant_id, route_name, route_path, enabled)
SELECT id, 'Dashboard', '/dashboard', true FROM tenants WHERE email = 'info@defaultchannel.com' UNION ALL
SELECT id, 'Customers', '/customers', true FROM tenants WHERE email = 'info@defaultchannel.com' UNION ALL
SELECT id, 'Applications', '/applications', true FROM tenants WHERE email = 'info@defaultchannel.com' UNION ALL
SELECT id, 'Documents', '/documents', true FROM tenants WHERE email = 'info@defaultchannel.com' UNION ALL
SELECT id, 'Settings', '/settings', true FROM tenants WHERE email = 'info@defaultchannel.com'
ON CONFLICT (tenant_id, route_name) DO NOTHING;

-- 9. Seed Tenant-Level Permissions
INSERT INTO permissions (permission_name, permission_key, description) VALUES
('View Dashboard', 'VIEW_DASHBOARD', 'Allows viewing of tenant dashboard metrics'),
('Manage Tenant Users', 'MANAGE_USERS', 'Allows creating, updating, and disabling tenant users'),
('Manage Tenant Roles', 'MANAGE_ROLES', 'Allows modifying tenant-level roles and permissions'),
('View Customers', 'VIEW_CUSTOMERS', 'Allows viewing customer records'),
('Manage Customers', 'MANAGE_CUSTOMERS', 'Allows creating and editing customer profiles'),
('View Applications', 'VIEW_APPLICATIONS', 'Allows viewing onboarding applications'),
('Manage Applications', 'MANAGE_APPLICATIONS', 'Allows creating, editing, and deleting applications'),
('Submit Applications', 'SUBMIT_APPLICATIONS', 'Allows submitting applications for review'),
('Review Applications', 'REVIEW_APPLICATIONS', 'Allows moving applications to review stage and verifying data'),
('Approve Applications', 'APPROVE_APPLICATIONS', 'Allows final approval or rejection of applications'),
('Upload Documents', 'UPLOAD_DOCUMENTS', 'Allows uploading customer identity and supporting documents'),
('View Documents', 'VIEW_DOCUMENTS', 'Allows viewing and downloading customer documents')
ON CONFLICT (permission_key) DO NOTHING;

-- 10. Seed Custom Tenant Roles for Default Tenant
INSERT INTO roles (tenant_id, role_name, description, is_system_role)
SELECT id, 'Channel Admin', 'Tenant Administrator with all permissions', true FROM tenants WHERE email = 'info@defaultchannel.com' UNION ALL
SELECT id, 'Branch Manager', 'Manager responsible for branch operations and applications', true FROM tenants WHERE email = 'info@defaultchannel.com' UNION ALL
SELECT id, 'Reviewer', 'Operations user responsible for verifying and reviewing applications', true FROM tenants WHERE email = 'info@defaultchannel.com' UNION ALL
SELECT id, 'Operations Executive', 'Executive handling documents verification and validation workflows', true FROM tenants WHERE email = 'info@defaultchannel.com' UNION ALL
SELECT id, 'Sales Executive', 'Sales staff creating customers and starting applications', true FROM tenants WHERE email = 'info@defaultchannel.com'
ON CONFLICT (tenant_id, role_name) DO NOTHING;

-- 11. Map Permissions to Custom Tenant Roles
-- Channel Admin: All permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.role_name = 'Channel Admin'
ON CONFLICT DO NOTHING;

-- Branch Manager: View Dashboard, View/Manage Customers, View/Manage/Submit Applications, Upload/View Documents
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.role_name = 'Branch Manager'
  AND p.permission_key IN (
      'VIEW_DASHBOARD', 'VIEW_CUSTOMERS', 'MANAGE_CUSTOMERS',
      'VIEW_APPLICATIONS', 'MANAGE_APPLICATIONS', 'SUBMIT_APPLICATIONS',
      'UPLOAD_DOCUMENTS', 'VIEW_DOCUMENTS'
  )
ON CONFLICT DO NOTHING;

-- Reviewer: View Dashboard, View Customers, View Applications, Review Applications, View Documents
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.role_name = 'Reviewer'
  AND p.permission_key IN (
      'VIEW_DASHBOARD', 'VIEW_CUSTOMERS', 'VIEW_APPLICATIONS',
      'REVIEW_APPLICATIONS', 'VIEW_DOCUMENTS'
  )
ON CONFLICT DO NOTHING;

-- Operations Executive: View Dashboard, View/Manage Customers, View/Manage/Submit Applications, Upload/View Documents
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.role_name = 'Operations Executive'
  AND p.permission_key IN (
      'VIEW_DASHBOARD', 'VIEW_CUSTOMERS', 'MANAGE_CUSTOMERS',
      'VIEW_APPLICATIONS', 'MANAGE_APPLICATIONS', 'SUBMIT_APPLICATIONS',
      'UPLOAD_DOCUMENTS', 'VIEW_DOCUMENTS'
  )
ON CONFLICT DO NOTHING;

-- Sales Executive: View Dashboard, View/Manage Customers, View/Manage/Submit Applications, Upload/View Documents
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.role_name = 'Sales Executive'
  AND p.permission_key IN (
      'VIEW_DASHBOARD', 'VIEW_CUSTOMERS', 'MANAGE_CUSTOMERS',
      'VIEW_APPLICATIONS', 'MANAGE_APPLICATIONS', 'SUBMIT_APPLICATIONS',
      'UPLOAD_DOCUMENTS', 'VIEW_DOCUMENTS'
  )
ON CONFLICT DO NOTHING;

-- 12. Create Sample Channel Admin User
-- Password: ChannelAdminPassword123!
INSERT INTO users (tenant_id, username, email, password_hash, status, first_name, last_name, phone)
SELECT
    t.id,
    'channeladmin',
    'admin@defaultchannel.com',
    crypt('ChannelAdminPassword123!', gen_salt('bf', 10)),
    'ACTIVE',
    'Default',
    'Channel Admin',
    '+919876543211'
FROM tenants t
WHERE t.email = 'info@defaultchannel.com'
ON CONFLICT (tenant_id, username) DO NOTHING;

-- 13. Assign Channel Admin Role to Sample User
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN tenants t ON u.tenant_id = t.id
CROSS JOIN roles r
WHERE t.email = 'info@defaultchannel.com'
  AND u.username = 'channeladmin'
  AND r.role_name = 'Channel Admin'
ON CONFLICT DO NOTHING;

COMMIT;

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('015_create_seed_data.sql') ON CONFLICT DO NOTHING;
