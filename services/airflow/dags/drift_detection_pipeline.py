import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
    'owner'                 : 'airflow',
    'description'           : 'Daily drift detection pipeline',
    'depend_on_past'        : False,
    'start_date'            : datetime(2024, 1, 1),
    'email_on_failure'      : False,
    'email_on_retry'        : False,
    'retries'               : 1,
    'retry_delay'           : timedelta(minutes=5)
}

with DAG('drift_detection_pipeline', default_args=default_args, schedule_interval="0 2 * * *", catchup=False) as dag:
    start_dag = DummyOperator(
        task_id='start_dag'
        )

    end_dag = DummyOperator(
        task_id='end_dag'
        )
    
    t1 = BashOperator(
        task_id='print_current_date',
        bash_command='date'
        )
        
    t2 = DockerOperator(
        task_id='derift_detection_task',
        image='drift_detection',
        container_name='drift_detection',
        api_version='auto',
        auto_remove=True,
        command="",
        environment={
                  'POSTGRES_HOST': 'postgres', #os.environ["POSTGRES_HOST"],
                  'PG_APP_PWD': os.environ["PG_APP_PWD"],
                },
        docker_url="tcp://docker-proxy:2375",
        network_mode="container:postgres-server",
        mount_tmp_dir = False
        )

    t3 = BashOperator(
        task_id='print_hello',
        bash_command='echo "hello world"'
        )
    
    start_dag >> t1 
    
    t1 >> t2 >> t3

    t3 >> end_dag
    