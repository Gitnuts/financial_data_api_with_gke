FROM python:3.9

RUN curl https://sdk.cloud.google.com > install_google_cloud_sdk.sh
RUN umask 0002; bash install_google_cloud_sdk.sh --disable-prompts --install-dir /cloud_sdk
ENV PATH $PATH:/cloud_sdk/google-cloud-sdk/bin

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY gcp_credentials.json /usr/src/app/gcp_credentials.json
COPY extract_30_to_20_day_options.sh /usr/src/app/exec.sh
COPY extract_option_values.py /usr/src/app/extract_option_values.py
COPY get_option_strikes.py /usr/src/app/get_option_strikes.py

COPY pythonclient/ /usr/src/app/pythonclient/
WORKDIR /usr/src/app/pythonclient
RUN python setup.py install
RUN pip install ibapi

RUN chmod +x /usr/src/app/exec.sh
WORKDIR /usr/src/app/

ENTRYPOINT ["/usr/src/app/exec.sh"]
