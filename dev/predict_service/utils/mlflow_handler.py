import os
import mlflow.sklearn
from typing import Tuple
from pprint import pprint
from utils.logger import logger
from mlflow.client import MlflowClient
from mlflow.pyfunc import PyFuncModel

class MLflowHandler:
    def __init__(self) -> None:
        tracking_uri = "http://localhost:5000" #os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000") #
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient(tracking_uri=tracking_uri)

    def check_mlflow_health(self) -> None:
        try:
            experiments = mlflow.search_experiments()
            for rm in experiments:
                pprint(dict(rm), indent=4)
                return "Service returning experiments"
        except:
            return "Error calling MLflow"

    def get_production_model(self, model_name: str) -> Tuple[PyFuncModel, str, str]:
        logger.info("Loading model from MLflow")
        data = self.client.search_registered_models(filter_string=f"name='{model_name}'")[0]
        model = mlflow.sklearn.load_model(f"models:/{model_name}@champion")
        return model, model_name, data.aliases