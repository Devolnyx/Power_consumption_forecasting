from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import datetime

import sys
import os

project_path = os.path.abspath(os.path.curdir)

default_args = {
    "owner": "Devolnyx",
    "start_date": days_ago(0),
    "retries": 1,
    "retry_delay": datetime.timedelta(seconds=10),
    "task_concurency": 2
}


pipelines = {"onestep": {"schedule": "1,31 * * * *"},  # At minute 1 and 31
            "multistep": {"schedule": "1,31 * * * *"}}  # At 23:48 every day - 3 hours diff

with DAG(
            default_args=default_args,
            dag_id="docker_dag",
            schedule_interval="1,31 * * * *"
    ) as dag:

    for task, params in pipelines.items():

        globals()['train_'+task] = BashOperator(
            task_id='train_' + task,
            bash_command=f'python3 /opt/airflow/train_' + task + '.py' #python3 /opt/airflow/app/train_' + task + '.py'
        )

        globals()['predict_'+task] = BashOperator(
            task_id='predict_' + task,
            bash_command=f'python3 /opt/airflow/predict_' + task + '.py' #'python3 /opt/airflow/app/predict_' + task + '.py'
        )

        globals()['train_' + task] >> globals()['predict_'+task]