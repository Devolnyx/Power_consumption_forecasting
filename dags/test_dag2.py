from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import datetime

import sys
import os

project_path = os.path.abspath(os.path.curdir)

default_args = {
    "owner": "Devolnyx",
    "start_date": days_ago(1),  # запуск день назад
    "retries": 1,  # запуск таска до 5 раз, если ошибка
    "retry_delay": datetime.timedelta(seconds=10),
    "task_concurency": 1  # одновременно только 1 таск
}


with DAG(
        default_args=default_args,
        dag_id="dag_with_python_dependencies_v05",
        schedule_interval='@daily'
) as dag:
    task1 = BashOperator(
        task_id='train',
        bash_command=f'cd {project_path} && python3 train_onestep.py'
    )

    task2 = BashOperator(
        task_id='predict',
        bash_command=f'cd {project_path} && python3 predict_onestep.py'
    )

    task1 >> task2
