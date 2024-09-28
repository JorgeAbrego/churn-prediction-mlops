import os
import pandas as pd
from time import sleep
from sqlalchemy import create_engine
from utils.logger import logger
from utils.mlflow_handler import MLflowHandler

logger.info("Predict job started")

POSTGRES_HOST = "localhost" #os.getenv('POSTGRES_HOST')
POSTGRES_PASSWORD = "app-p4ss" #os.getenv('PG_APP_PWD')
DB_CONNECTION_URL = f"postgresql://app_user:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/app_db"

mlf = MLflowHandler()

def get_data_from_db(query):
    try:
        engine = create_engine(DB_CONNECTION_URL)
        with engine.connect() as connection:
            data = pd.read_sql(query, connection)
        logger.info("Data retrieved from database successfully.")
        return data
    except Exception as e:
        logger.error(f"Error retrieving data from database: {e}")
        return None

def preprocess_data(data):
    cat_cols = ['gender', 'MultipleLines', 'InternetService', 'OnlineSecurity', 
            'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 
            'StreamingMovies', 'Contract', 'PaymentMethod']
    num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
    bin_cols = ['SeniorCitizen', 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling']
    dataset = (data
    .drop_duplicates(keep='first')
    .drop(index=data[data['TotalCharges'] == ' '].index)
    [cat_cols + num_cols + bin_cols]
    .assign(Partner = lambda x: x.Partner.map({'Yes': 1, 'No': 0}),
            Dependents = lambda x: x.Dependents.map({'Yes': 1, 'No': 0}),
            PhoneService = lambda x: x.PhoneService.map({'Yes': 1, 'No': 0}),
            PaperlessBilling = lambda x: x.PaperlessBilling.map({'Yes': 1, 'No': 0})
            )
    )
    return dataset
    
def get_model(model_name: str):
    model_name = f"{model_name}"
    model, model_name, model_version = mlf.get_production_model(
        model_name=model_name
    )
    return model, model_name, model_version

def save_data(data):
    try:
        engine = create_engine(DB_CONNECTION_URL)
        with engine.connect() as connection:
            data.to_sql('prediction_logs', connection, if_exists='append', index=False)
        logger.info("Data saved to database successfully.")
    except Exception as e:
        logger.error(f"Error saving data to database: {e}")
    
def predict(query, model):
    mlf.check_mlflow_health()
    data = get_data_from_db(query)
    if len(data)==0:
        logger.warning(f"No records found. Skipping prediction")
        return None
    dataset = preprocess_data(data)
    logger.info("Preprocessing completed")
    model, model_name, model_alias = get_model(model_name=model)
    if model is None:
        logger.error("Model not found, skipping prediction")
        return None
    y = model.predict(dataset)
    y_prob = model.predict_proba(dataset)
    #print(f"{model_name}, {model_alias}")
    logger.info("Model prediction completed")
    data['prediction'] = y
    data['probability'] = y_prob[:, 1]
    data['model_name'] = model_name
    data['model_version'] = model_alias
    save_data(data)
    sleep(3)
    logger.info("Predict job completed")
    return None

if __name__ == "__main__":
    query = "SELECT * FROM customer_data ORDER BY random() LIMIT 10" 
    MODEL_NAME = "telco_customer_churn" 
    result = predict(query, MODEL_NAME)