#!/bin/bash
set -e

# Check if environment variables are defined
if [ -z "$PG_AIRFLOW_PWD" ] || [ -z "$PG_MLFLOW_PWD" ] || [ -z "$PG_APP_PWD" ]; then
  echo "ERROR: One or more environment variables for passwords are not defined."
  exit 1
fi

# Create users and databases
PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER airflow_user WITH PASSWORD '$PG_AIRFLOW_PWD' CREATEDB;
    CREATE DATABASE airflow_db
        WITH 
        OWNER = airflow_user
        ENCODING = 'UTF8'
        LC_COLLATE = 'en_US.utf8'
        LC_CTYPE = 'en_US.utf8'
        TABLESPACE = pg_default;
    GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow_user;

    CREATE USER mlflow_user WITH PASSWORD '$PG_MLFLOW_PWD' CREATEDB;
    CREATE DATABASE mlflow_db
        WITH 
        OWNER = mlflow_user
        ENCODING = 'UTF8'
        LC_COLLATE = 'en_US.utf8'
        LC_CTYPE = 'en_US.utf8'
        TABLESPACE = pg_default;
    GRANT ALL PRIVILEGES ON DATABASE mlflow_db TO mlflow_user;

    CREATE USER app_user WITH PASSWORD '$PG_APP_PWD' CREATEDB;
    CREATE DATABASE app_db
        WITH 
        OWNER = app_user
        ENCODING = 'UTF8'
        LC_COLLATE = 'en_US.utf8'
        LC_CTYPE = 'en_US.utf8'
        TABLESPACE = pg_default;
    GRANT ALL PRIVILEGES ON DATABASE app_db TO app_user;
EOSQL