-- auth: initial schema (user, credential, session)
-- Branch: auth | Revision: 0001 (up)
-- Applied by scripts/migrate_sql.py and tracked in schema_migrations.

CREATE TABLE auth_user (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR(320),
    is_active   BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_auth_user_email UNIQUE (email)
);

CREATE TABLE auth_credential (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER     NOT NULL REFERENCES auth_user (id) ON DELETE CASCADE,
    channel      VARCHAR(32) NOT NULL,
    secret_hash  VARCHAR(255)
);
CREATE INDEX ix_auth_credential_user_id ON auth_credential (user_id);

CREATE TABLE auth_session (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER      NOT NULL REFERENCES auth_user (id) ON DELETE CASCADE,
    refresh_token_hash  VARCHAR(255) NOT NULL,
    revoked             BOOLEAN      NOT NULL DEFAULT FALSE,
    expires_at          TIMESTAMPTZ  NOT NULL
);
CREATE INDEX ix_auth_session_user_id ON auth_session (user_id);
