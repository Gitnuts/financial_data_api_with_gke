from datetime import timedelta, datetime
import os
import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from kubernetes.client import models as k8s
from airflow.providers.google.cloud.operators.kubernetes_engine import GKEStartPodOperator
from alerts_script import airflow_alerts, warnings

# To use this DAG, you need to specify:
# - project_id
# - location
# - cluster_name
# - namespace
# - image_pull_secrets

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1, hour=0, minute=0, second=0),  # set 1 day ago for one-per-day DAGs
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'wait_for_downstream': False,
}


with DAG(
    dag_id='binance_features_dag',
    default_args=default_args,
    description='Extracting data from Binance and storing to postgres database',
    schedule_interval="0 10 * * *",
    max_active_runs=1,
    catchup=False,
) as dag:

    kubernetes_pod = GKEStartPodOperator(
        task_id="binance_to_postgres",
        name="binance_to_postgres",
        project_id="project_id",
        location="europe-west1-b",
        cluster_name="cluster_name",
        namespace="airflow",
        image_pull_policy="Always",
        image_pull_secrets=[k8s.V1LocalObjectReference('kube')],
        image="eu-west1-docker.pkg.dev/cluster_name/repo/binance_features:1.0.0",
        get_logs=True,
        is_delete_operator_pod=True,
    )
