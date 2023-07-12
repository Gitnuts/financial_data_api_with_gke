#!/bin/bash

export EXECUTION_TIMESTAMP=$1
gcloud auth activate-service-account --quiet --key-file gcp_credentials.json

output=`python get_option_strikes.py`

date=`python3 -c "import json, sys; print(json.loads(sys.argv[1])[-1])" "$output"`

echo "Next expiration date is ${date}."
echo "Strikes are: ${output}."

if gsutil ls gs://bucket/options/SPY_30_to_20/call/SPY-${date}-C.csv >/dev/null 2>&1; then
    echo "File already exists!"
    python3 extract_option_values.py "$output" "C"
    python3 extract_option_values.py "$output" "P"
else
    python3 extract_option_values.py "$output" "C"
    python3 extract_option_values.py "$output" "P"
fi

file_size=$(stat -c %s SPY-${date}-C.csv)
if [ $file_size -lt 100 ]; then
  echo "File with call options is smaller than 100 B!"
else
  gsutil cp SPY-${date}-C.csv gs://bucket/options/SPY_30_to_20/call/SPY-${date}-C.csv
fi

file_size=$(stat -c %s SPY-${date}-P.csv)
if [ $file_size -lt 100 ]; then
  echo "File with put options is smaller than 100 B!"
else
  gsutil cp SPY-${date}-P.csv gs://bucket/options/SPY_30_to_20/put/SPY-${date}-P.csv
fi

exit 0
