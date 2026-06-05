-- Migration: 014_create_job_ledger.sql
-- Description: Create the job_ledger table.

-- Create job_ledger table
CREATE TABLE IF NOT EXISTS job_ledger (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING' NOT NULL,
    payload JSONB,
    error_message TEXT,
    retry_count INT DEFAULT 0 NOT NULL,
    max_retries INT DEFAULT 3 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_job_ledger_status CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED'))
);

-- Trigger to automatically update updated_at for job_ledger
CREATE TRIGGER trigger_update_job_ledger_updated_at
    BEFORE UPDATE ON job_ledger
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Indexes for performance and searchability
CREATE INDEX idx_job_ledger_tenant_id ON job_ledger(tenant_id);
CREATE INDEX idx_job_ledger_uuid ON job_ledger(uuid);
CREATE INDEX idx_job_ledger_status ON job_ledger(status);

-- Record the migration version
INSERT INTO schema_migrations (version) VALUES ('014_create_job_ledger.sql') ON CONFLICT DO NOTHING;
