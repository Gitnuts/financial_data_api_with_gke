#!/bin/bash

gcloud auth activate-service-account --key-file gcp_credentials.json

EXECUTION_TIMESTAMP=$(date --date="yesterday" +'%d_%b_%Y')
BUCKET_NAME="binance_features"

# If bucket "binance_features" exists:
python binance_features.py -s y
gsutil cp output.csv gs://bucket/features/"$BUCKET_NAME"/binance_features_"$EXECUTION_TIMESTAMP".csv

# Check if "binance_features" table exists.
# If it doesn't, transfer all data from GCS to postgres.
# This is essentially important if data is lost from GSE persistent volume

python check_table.py "$BUCKET_NAME"
test $? -ne 0 && echo "Exporting from GCS to postgres..." \
  && python gcs_to_postgres.py \
  && exit 0

# If it does, transfer only the recent one, i.e output.csv
echo "Uploading data to the PostgreSQL database..."
python upload_postgres.py "$BUCKET_NAME"

exit 0
