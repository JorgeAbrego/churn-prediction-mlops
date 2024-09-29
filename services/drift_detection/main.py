import os
import pandas as pd
from time import sleep
from sqlalchemy import create_engine
from utils.logger import logger
from utils.mlflow_handler import MLflowHandler
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from datetime import datetime, timedelta

logger.info("Drift detection job started")

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PASSWORD = os.getenv('PG_APP_PWD')
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

def get_reference_data(model_name):
    tmp_path = mlf.get_reference_data(model_name=model_name)
    df = pd.read_csv(tmp_path).drop(columns='Churn')
    return df

def save_data(data, table_name):
    try:
        engine = create_engine(DB_CONNECTION_URL)
        with engine.connect() as connection:
            data.to_sql(table_name, connection, if_exists='append', index=False)
        logger.info(f"Data saved to table '{table_name}' successfully.")
    except Exception as e:
        logger.error(f"Error saving data to table '{table_name}': {e}")

def drift_detection(query, model, execution_date):
    logger.info("Drift detection job started")
    logger.info("Get data from database")
    df_tst = (get_data_from_db(query)
          [['gender', 'MultipleLines', 'InternetService', 'OnlineSecurity',
            'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV',
            'StreamingMovies', 'Contract', 'PaymentMethod', 'tenure', 
            'MonthlyCharges', 'TotalCharges', 'SeniorCitizen', 'Partner',
            'Dependents', 'PhoneService', 'PaperlessBilling']]
         )
    print(df_tst.head(2))
    logger.info("Get reference data")
    df_ref = get_reference_data(model)
    print(df_ref.head(2))
    logger.info("Start drift detection")
    cat_cols = ['gender', 'MultipleLines', 'InternetService', 'OnlineSecurity', 
            'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 
            'StreamingMovies', 'Contract', 'PaymentMethod']
    num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
    bin_cols = ['SeniorCitizen', 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling']
    column_mapping = ColumnMapping(
        numerical_features=num_cols,
        categorical_features=cat_cols+bin_cols,
        target=None
    )
    report = Report(metrics = [DataDriftPreset(drift_share=0.25, cat_stattest_threshold=0.2, num_stattest_threshold=0.2)])
    logger.info("Start drift report")
    report.run(reference_data=df_ref, current_data=df_tst, column_mapping=column_mapping)
    report_dict = report.as_dict()
    result = report_dict["metrics"][0]["result"]
    df_rpt = (pd.DataFrame([result])
                  .assign(date_dataset=execution_date,
                          date_report=execution_date)
                  )
    save_data(df_rpt, 'data_report')
    logger.info("Save drift report")
    lst = []
    for key in report_dict["metrics"][1]["result"]['drift_by_columns'].keys():
        lst.append([report_dict["metrics"][1]["result"]['drift_by_columns'][key]['column_name'],
                    report_dict["metrics"][1]["result"]['drift_by_columns'][key]['column_type'],
                    report_dict["metrics"][1]["result"]['drift_by_columns'][key]['drift_score'],
                    report_dict["metrics"][1]["result"]['drift_by_columns'][key]['drift_detected']]
                    )
    df_cols = (pd.DataFrame(lst)
               .rename(columns={0:'column_name', 1:'column_type', 2:'drift_score', 3:'drift_detected'})
               .assign(date_dataset=execution_date,
                          date_report=execution_date)
              )
    save_data(df_cols, 'data_columns_report')
    logger.info("Save drift columns report")
    logger.info("Drift detection job completed")
    return None


if __name__ == "__main__":
    execution_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    query = f"""SELECT * 
                FROM prediction_logs
                WHERE DATE(prediction_date) = '{execution_date}'
            """
    MODEL_NAME = "telco_customer_churn" 
    result = drift_detection(query, MODEL_NAME, execution_date)