-- Migration: 012_create_documents.sql
-- Description: Create the documents table, enable RLS, and define RLS policies.

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
    customer_id BIGINT REFERENCES customers(id) ON DELETE CASCADE NOT NULL,
    application_id BIGINT REFERENCES applications(id) ON DELETE CASCADE NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    verification_status VARCHAR(50) DEFAULT 'UNVERIFIED' NOT NULL,
    verified_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    rejection_reason TEXT,
    uploaded_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_document_verification_status CHECK (verification_status IN ('UNVERIFIED', 'VERIFIED', 'REJECTED'))
);

-- Trigger to automatically update updated_at for documents
CREATE TRIGGER trigger_update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Indexes for performance and relationships
CREATE INDEX idx_documents_tenant_id ON documents(tenant_id);
CREATE INDEX idx_documents_customer_id ON documents(customer_id);
CREATE INDEX idx_documents_application_id ON documents(application_id);
CREATE INDEX idx_documents_uuid ON documents(uuid);
CREATE INDEX idx_documents_verification_status ON documents(verification_status);

-- Enable Row Level Security (RLS)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create tenant isolation policy
CREATE POLICY tenant_isolation_policy ON documents
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::BIGINT)
    WITH CHECK (tenant_id = current_setting('app.tenant_id')::BIGINT);

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('012_create_documents.sql') ON CONFLICT DO NOTHING;
