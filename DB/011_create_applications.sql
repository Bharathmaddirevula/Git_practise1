-- Migration: 011_create_applications.sql
-- Description: Create the applications table, enable RLS, and define RLS policies.

-- Create applications table
CREATE TABLE IF NOT EXISTS applications (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
    customer_id BIGINT REFERENCES customers(id) ON DELETE CASCADE NOT NULL,
    application_number VARCHAR(100) NOT NULL,
    application_type VARCHAR(100) NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'DRAFT' NOT NULL,
    assigned_to BIGINT REFERENCES users(id) ON DELETE SET NULL,
    reviewed_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    approved_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    rejection_reason TEXT,
    review_started_at TIMESTAMPTZ,
    decision_date TIMESTAMPTZ,
    created_by BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT uq_applications_tenant_app_num UNIQUE (tenant_id, application_number),
    CONSTRAINT chk_application_status CHECK (status IN ('DRAFT', 'SUBMITTED', 'REVIEW', 'APPROVED', 'REJECTED'))
);

-- Trigger to automatically update updated_at for applications
CREATE TRIGGER trigger_update_applications_updated_at
    BEFORE UPDATE ON applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Indexes for performance, searchability, and relationships
CREATE INDEX idx_applications_tenant_id ON applications(tenant_id);
CREATE INDEX idx_applications_customer_id ON applications(customer_id);
CREATE INDEX idx_applications_uuid ON applications(uuid);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_assigned_to ON applications(assigned_to);

-- Enable Row Level Security (RLS)
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Create tenant isolation policy
CREATE POLICY tenant_isolation_policy ON applications
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::BIGINT)
    WITH CHECK (tenant_id = current_setting('app.tenant_id')::BIGINT);

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('011_create_applications.sql') ON CONFLICT DO NOTHING;
