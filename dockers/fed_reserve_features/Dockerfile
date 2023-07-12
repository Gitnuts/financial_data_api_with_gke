FROM python:3.9

RUN curl https://sdk.cloud.google.com > install_google_cloud_sdk.sh
RUN umask 0002; bash install_google_cloud_sdk.sh --disable-prompts --install-dir /cloud_sdk
ENV PATH $PATH:/cloud_sdk/google-cloud-sdk/bin

#RUN apt-get update && \
#    apt-get install -y kafkacat jq

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY gcp_credentials.json /usr/src/app/gcp_credentials.json
COPY features_import.py /usr/src/app/features_import.py
COPY check_table.py /usr/src/app/check_table.py
COPY upload_postgres.py /usr/src/app/upload_postgres.py
COPY gcs_to_postgres.py /usr/src/app/gcs_to_postgres.py
COPY postgresdb.ini /usr/src/app/postgresdb.ini
COPY exec.sh /usr/src/app/exec.sh

RUN chmod +x /usr/src/app/exec.sh
WORKDIR /usr/src/app/

ENV FRED_API_KEY='your_fred_api_key

ENTRYPOINT ["/usr/src/app/exec.sh"]
