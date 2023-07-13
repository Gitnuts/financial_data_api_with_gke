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

EXECUTION_DATE = '{{ execution_date }}'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(2, hour=0, minute=0, second=0),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'wait_for_downstream': False,
}


with DAG(
    dag_id='extract_spy_options',
    default_args=default_args,
    description='extract_spy_options',
    schedule_interval="0 9 * * 1-5",
    max_active_runs=1,
    catchup=False,
) as dag:

    extracting_30_to_20_day_options = GKEStartPodOperator(
        task_id="extracting_30_to_20_day_options",
        name="extracting_30_to_20_day_options",
        project_id="project_id",
        location="europe-west1-b",
        cluster_name="cluster_name",
        namespace="airflow",
        image_pull_policy="Always",
        image_pull_secrets=[k8s.V1LocalObjectReference('kube')],
        image="eu-west1-docker.pkg.dev/cluster_name/repo/ib_spy_options:1.0.0",
        get_logs=True,
        is_delete_operator_pod=True,
        arguments=[EXECUTION_DATE]
    )
    
