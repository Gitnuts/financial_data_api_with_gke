# Financial APIs using Google Kubernetes Engine

This repository serves as a small showcase of financial APIs. In this example, we install four different APIs (Interactive Brokers, Binance API, TradingView, and Federal Reserve) as data pipelines in Apache Airflow. Apache Airflow, along with other necessary services for API workflows, is provisioned on GKE (Google Kubernetes Engine). Finally, data is stored in postgreSQL database that is mounted to VM's persistent volume while GCS (Google Cloud Storage) works as a backup for the data.

