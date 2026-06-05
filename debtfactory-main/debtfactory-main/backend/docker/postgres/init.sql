-- Postgres initialization: database + extensions.
-- Runs once on first container start (docker-entrypoint-initdb.d).

-- Create the application database if it does not already exist.
SELECT 'CREATE DATABASE loan_platform'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'loan_platform')\gexec

\connect loan_platform

-- Extensions used across services.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
