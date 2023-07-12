#!/bin/bash

gcloud auth activate-service-account --key-file gcp_credentials.json

EXECUTION_TIMESTAMP=$(date --date="yesterday" +'%d_%b_%Y')
BUCKET_NAME="btc_features"
SINGLE=1

# Check if GCS bucket exists. If it doesn't, the program will download Fed's data from 2010-01-01.
# Otherwise it will download only yesterday's data.
echo "Checking if bucket exists..."
gsutil ls gs://bucket/features/ | grep "$BUCKET_NAME"
test $? -ne 0 && echo "Bucket $BUCKET_NAME doesn't exist" && SINGLE=0

python3 features_import.py $SINGLE
gsutil cp output.csv gs://bucket/features/btc_features/btc_features_"$EXECUTION_TIMESTAMP".csv

# Check if "btc_features" table exists.
# If it doesn't, transfer all data from GCS to postgres.
# This is essentially important if data is lost from GSE persistent volume.
python check_table.py "$BUCKET_NAME"
test $? -ne 0 && echo "Exporting from GCS to postgres..." \
  && python gcs_to_postgres.py "$BUCKET_NAME"\
  && exit 0

echo "Uploading data to the PostgreSQL database..."
python upload_postgres.py "$BUCKET_NAME"
exit 0
