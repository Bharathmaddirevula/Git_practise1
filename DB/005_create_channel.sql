-- Migration: 005_create_tenants.sql
-- Description: Create the tenants (channels) table.

-- Create tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    tenant_name VARCHAR(150) NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    gst_number VARCHAR(15),
    pan_number VARCHAR(10),
    address TEXT,
    status VARCHAR(50) DEFAULT 'PENDING' NOT NULL,
    domain_name VARCHAR(255) UNIQUE,
    logo_url VARCHAR(512),
    primary_color VARCHAR(7) DEFAULT '#0F172A',
    secondary_color VARCHAR(7) DEFAULT '#3B82F6',
    timezone VARCHAR(100) DEFAULT 'UTC' NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR' NOT NULL,
    support_email VARCHAR(255),
    created_by BIGINT REFERENCES super_admins(id) ON DELETE SET NULL,
    approved_by BIGINT REFERENCES super_admins(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_tenant_status CHECK (status IN ('PENDING', 'ACTIVE', 'SUSPENDED', 'REJECTED'))
);

-- Trigger to automatically update updated_at for tenants
CREATE TRIGGER trigger_update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Indexes for performance and searchability
CREATE INDEX idx_tenants_email ON tenants(email);
CREATE INDEX idx_tenants_uuid ON tenants(uuid);
CREATE INDEX idx_tenants_status ON tenants(status);
CREATE INDEX idx_tenants_domain ON tenants(domain_name);

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('005_create_tenants.sql') ON CONFLICT DO NOTHING;
