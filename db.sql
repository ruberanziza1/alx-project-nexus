


-- Create the user with your exact password
CREATE USER ecommerce_user WITH PASSWORD 'yourdbName';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO ecommerce_user;

-- Grant permissions on existing tables and sequences (if any)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ecommerce_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ecommerce_user;

-- Grant permissions on future tables and sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ecommerce_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ecommerce_user;

-- Make user able to create databases (optional, for Django migrations)
ALTER USER ecommerce_user CREATEDB;