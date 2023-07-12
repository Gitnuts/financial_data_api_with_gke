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
    'start_date': airflow.utils.dates.days_ago(1, hour=0, minute=0, second=0),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'wait_for_downstream': False,
}


with DAG(
    dag_id='Feds_and_bitcoin_features_dag_from_git',
    default_args=default_args,
    description='Extracting data from TradingView, transferring via Kafka service,'
                'merging with Feds data and storing to PostgreSQL database',
    schedule_interval="0 5 * * *",
    max_active_runs=1,
    catchup=False,
) as dag:

    tradingview_to_kafka = GKEStartPodOperator(
        task_id="tradingview_to_kafka",
        name="tradingview-to-kafka",
        project_id="project_id",
        location="europe-west1-b",
        cluster_name="cluster_name",
        namespace="airflow",
        image_pull_policy="Always",
        image_pull_secrets=[k8s.V1LocalObjectReference('kube')],
        image="eu-west1.pkg.dev/cluster_name/repo/tradingview-to-kafka:1.0.0",
        get_logs=True,
        is_delete_operator_pod=True,
    )

    fed_assets_to_postgres = GKEStartPodOperator(
        task_id="fed_assets_to_postgres",
        name="fed_assets_to_postgres",
        project_id="project_id",
        location="europe-west1-b",
        cluster_name="cluster_name",
        namespace="airflow",
        image_pull_policy="Always",
        image_pull_secrets=[k8s.V1LocalObjectReference('kube')],
        image="eu-west1-docker.pkg.dev/cluster_name/repo/fed-assets-to-postgres:1.0.0",
        get_logs=True,
        is_delete_operator_pod=True,
    )

tradingview_to_kafka >> fed_assets_to_postgres

