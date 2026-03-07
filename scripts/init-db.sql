-- Solstein Database Initialization Script
-- Run automatically when PostgreSQL container starts

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Database and user are created via environment variables
-- This script runs after the database is initialized

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON DATABASE solstein TO postgres;
