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

# Create table in prediction_db
PGPASSWORD=$PG_APP_PWD psql -v ON_ERROR_STOP=1 --username "app_user" --dbname "app_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS customer_data (
        "customerID" TEXT,
        "gender" TEXT,
        "SeniorCitizen" INTEGER,
        "Partner" VARCHAR,
        "Dependents" VARCHAR,
        "tenure" INTEGER,
        "PhoneService" VARCHAR,
        "MultipleLines" VARCHAR,
        "InternetService" VARCHAR,
        "OnlineSecurity" VARCHAR,
        "OnlineBackup" VARCHAR,
        "DeviceProtection" VARCHAR,
        "TechSupport" VARCHAR,
        "StreamingTV" VARCHAR,
        "StreamingMovies" VARCHAR,
        "Contract" VARCHAR,
        "PaperlessBilling" VARCHAR,
        "PaymentMethod" VARCHAR,
        "MonthlyCharges" FLOAT,
        "TotalCharges" FLOAT NULL,
        "Churn" VARCHAR
    );


    CREATE TABLE IF NOT EXISTS prediction_logs (
        "customerID" TEXT,
        "gender" TEXT,
        "SeniorCitizen" INTEGER,
        "Partner" VARCHAR,
        "Dependents" VARCHAR,
        "tenure" INTEGER,
        "PhoneService" VARCHAR,
        "MultipleLines" VARCHAR,
        "InternetService" VARCHAR,
        "OnlineSecurity" VARCHAR,
        "OnlineBackup" VARCHAR,
        "DeviceProtection" VARCHAR,
        "TechSupport" VARCHAR,
        "StreamingTV" VARCHAR,
        "StreamingMovies" VARCHAR,
        "Contract" VARCHAR,
        "PaperlessBilling" VARCHAR,
        "PaymentMethod" VARCHAR,
        "MonthlyCharges" FLOAT,
        "TotalCharges" FLOAT NULL,
        "Churn" VARCHAR,
        "prediction" INTEGER,
        "probability" FLOAT,
        "model_name" VARCHAR,
        "model_version" VARCHAR,
        "prediction_date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE data_report (
        drift_share FLOAT,
        number_of_columns INTEGER,
        number_of_drifted_columns INTEGER,
        share_of_drifted_columns FLOAT,
        dataset_drift BOOLEAN,
        date_dataset DATE,
        date_report DATE
    );

    CREATE TABLE data_columns_report (
        column_name VARCHAR,
        column_type VARCHAR,
        drift_score FLOAT,
        drift_detected BOOLEAN,
        date_dataset DATE,
        date_report DATE
    );
EOSQL

PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \c app_db;

    COPY customer_data
    FROM '/tmp/data.csv' 
    DELIMITER ',' 
    CSV HEADER
    NULL AS ' ';
EOSQL