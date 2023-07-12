#!/bin/bash

gcloud auth activate-service-account --key-file gcp_credentials.json

yesterday=$(date --date="yesterday" +'%a, %d %b %Y')

start_date=$(date -d "2018-01-01" "+%s")
end_date=$(date -d "yesterday" "+%s")
all_days=$(( (end_date - start_date) / 86400 ))
all_days=$(( all_days + 2 ))


EXECUTION_TIMESTAMP=$(date --date="yesterday" +'%d_%b_%Y')
BUCKET_NAME="btc_features"
DAYS=2

echo "Checking if bucket exists..."
gsutil ls gs://bucket/features/ | grep "$BUCKET_NAME"
test $? -ne 0 && echo "Bucket $BUCKET_NAME doesn't exist." && DAYS=$all_days \
  && echo "Collecting data from $DAYS days ago, i.e from 2018-01-01"

# Two examples:

# 1) BTC.D:CRYPTOCAP  bitcoin_dominance
node kafka_producer.js \
CRYPTOCAP \
BTC.D \
1D \
RSI \
"$DAYS" \
'00:00:00 GMT' \
"$yesterday" \
bitcoin_dominance

# 2) BTC:CRYPTOCAP  bitcoin_market_cap
node kafka_producer.js \
CRYPTOCAP \
BTC \
1D \
RSI \
"$DAYS" \
'00:00:00 GMT' \
"$yesterday" \
bitcoin_market_cap

exit 0
