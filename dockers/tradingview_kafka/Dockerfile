FROM node:16


RUN curl https://sdk.cloud.google.com > install_google_cloud_sdk.sh
RUN umask 0002; bash install_google_cloud_sdk.sh --disable-prompts --install-dir /cloud_sdk
ENV PATH $PATH:/cloud_sdk/google-cloud-sdk/bin

RUN apt-get update && \
    apt-get install -y kafkacat


COPY @mathieuc/tradingview /usr/src/app/@mathieuc/tradingview
COPY @mathieuc/tradingview/package.json package.json
COPY kafka_producer.js usr/src/app/kafka_producer.js
COPY exec.sh usr/src/app/exec.sh

COPY gcp_credentials.json /usr/src/app/gcp_credentials.json

RUN chmod +x /usr/src/app/exec.sh
WORKDIR /usr/src/app/

RUN npm install kafkajs
RUN npm install

ENV KAFKAJS_NO_PARTITIONER_WARNING=1

ENTRYPOINT ["/usr/src/app/exec.sh"]
