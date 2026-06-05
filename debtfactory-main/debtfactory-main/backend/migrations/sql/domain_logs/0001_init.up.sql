-- domain_logs: initial schema (source, entry)
-- Branch: domain_logs | Revision: 0001 (up)
-- Applied by scripts/migrate_sql.py and tracked in schema_migrations.

CREATE TABLE domain_logs_source (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(128) NOT NULL,
    CONSTRAINT uq_domain_logs_source_name UNIQUE (name)
);

CREATE TABLE domain_logs_entry (
    id         SERIAL PRIMARY KEY,
    source_id  INTEGER     NOT NULL REFERENCES domain_logs_source (id) ON DELETE CASCADE,
    level      VARCHAR(16) NOT NULL,
    message    TEXT        NOT NULL,
    timestamp  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_domain_logs_entry_source_id ON domain_logs_entry (source_id);
