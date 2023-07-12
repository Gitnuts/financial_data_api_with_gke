FROM apache/airflow:2.3.0

USER root

RUN apt update && \
    curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl

# =================================== #
#   Installing IB API requirements    #
# =================================== #

COPY pythonclient/ ${AIRFLOW_HOME}/pythonclient/
WORKDIR ${AIRFLOW_HOME}/pythonclient
RUN python setup.py install

USER airflow

# ======================================== #
#   Installing Google cloud requirements   #
# ======================================== #

WORKDIR ${AIRFLOW_HOME}
RUN curl https://sdk.cloud.google.com > install_google_cloud_sdk.sh
RUN umask 0002; bash install_google_cloud_sdk.sh --disable-prompts --install-dir ${AIRFLOW_HOME}
RUN pip install ibapi

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY dags ${AIRFLOW_HOME}/dags
COPY gcp_credentials.json ${AIRFLOW_HOME}/gcp_credentials.json

ENV PATH $PATH:${AIRFLOW_HOME}/google-cloud-sdk/bin
ENV PATH $PATH:/usr/local/bin

RUN bash gcloud components install gke-gcloud-auth-plugin

WORKDIR ${AIRFLOW_HOME}
