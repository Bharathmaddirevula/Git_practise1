-- Migration: 009_create_tenant_limits_flags_routes.sql
-- Description: Create tenant_limits, tenant_feature_flags, and tenant_route_catalog tables.

-- Create tenant_limits table
CREATE TABLE IF NOT EXISTS tenant_limits (
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE PRIMARY KEY,
    max_users INT DEFAULT 10 NOT NULL,
    max_storage_gb INT DEFAULT 5 NOT NULL,
    max_api_calls INT DEFAULT 10000 NOT NULL,
    max_branches INT DEFAULT 1 NOT NULL
);

-- Index for tenant_limits tenant_id (PK, but explicit index is good practice)
CREATE INDEX idx_tenant_limits_tenant_id ON tenant_limits(tenant_id);

-- Create tenant_feature_flags table
CREATE TABLE IF NOT EXISTS tenant_feature_flags (
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    feature_name VARCHAR(100) NOT NULL,
    enabled BOOLEAN DEFAULT FALSE NOT NULL,
    PRIMARY KEY (tenant_id, feature_name)
);

-- Index for tenant_feature_flags
CREATE INDEX idx_tenant_feature_flags_tenant_id ON tenant_feature_flags(tenant_id);

-- Create tenant_route_catalog table
CREATE TABLE IF NOT EXISTS tenant_route_catalog (
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    route_name VARCHAR(150) NOT NULL,
    route_path VARCHAR(255) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE NOT NULL,
    PRIMARY KEY (tenant_id, route_name)
);

-- Index for tenant_route_catalog
CREATE INDEX idx_tenant_route_catalog_tenant_id ON tenant_route_catalog(tenant_id);

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('009_create_tenant_limits_flags_routes.sql') ON CONFLICT DO NOTHING;
