-- auth: rollback initial schema
-- Branch: auth | Revision: 0001 (down)

DROP TABLE IF EXISTS auth_session;
DROP TABLE IF EXISTS auth_credential;
DROP TABLE IF EXISTS auth_user;
