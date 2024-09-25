FROM python:3.10.14-slim-bullseye

LABEL maintainer="jorge.abrego@gmail.com"
LABEL version="1.0"
LABEL description="Dockerfile to configure an MLflow server, using a database as backend store and a storage for artifacts"

RUN apt-get update && apt-get -y upgrade \
    && apt-get install -y procps \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip --version    

RUN groupadd mlflow && useradd --create-home -g mlflow mlflow

ENV PATH /home/mlflow/.local/bin:${PATH}

WORKDIR /home/mlflow

COPY mlflow_requirements.txt mlflow_requirements.txt

RUN pip install --no-cache-dir -r mlflow_requirements.txt \
    && rm mlflow_requirements.txt

USER mlflow

EXPOSE 5000

CMD mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri ${BACKEND_STORE_URI} \
    --artifacts-destination s3://${MLFLOW_BUCKET_NAME} \
    --serve-artifacts