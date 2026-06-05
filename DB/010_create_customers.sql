-- Migration: 010_create_customers.sql
-- Description: Create the customers table, enable RLS, and define RLS policies.

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    annual_income NUMERIC(15, 2),
    occupation VARCHAR(100),
    pan_number VARCHAR(10),
    aadhaar_number VARCHAR(12),
    address TEXT,
    status VARCHAR(50) DEFAULT 'ACTIVE' NOT NULL,
    kyc_status VARCHAR(50) DEFAULT 'PENDING' NOT NULL,
    kyc_verified_at TIMESTAMPTZ,
    created_by BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT uq_customers_tenant_email UNIQUE (tenant_id, email),
    CONSTRAINT uq_customers_tenant_mobile UNIQUE (tenant_id, mobile),
    CONSTRAINT chk_kyc_status CHECK (kyc_status IN ('PENDING', 'VERIFIED', 'FAILED'))
);

-- Trigger to automatically update updated_at for customers
CREATE TRIGGER trigger_update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Indexes for performance, searchability, and relationships
CREATE INDEX idx_customers_tenant_id ON customers(tenant_id);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_uuid ON customers(uuid);
CREATE INDEX idx_customers_status ON customers(status);
CREATE INDEX idx_customers_kyc_status ON customers(kyc_status);

-- Enable Row Level Security (RLS)
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Create tenant isolation policy
CREATE POLICY tenant_isolation_policy ON customers
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::BIGINT)
    WITH CHECK (tenant_id = current_setting('app.tenant_id')::BIGINT);

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('010_create_customers.sql') ON CONFLICT DO NOTHING;
