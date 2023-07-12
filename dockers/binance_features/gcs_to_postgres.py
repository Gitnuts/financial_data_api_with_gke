from google.cloud import storage
import io
import pandas as pd
from upload_postgres import upload_to_postgres

# Initialise a client
storage_client = storage.Client.from_service_account_json("gcp_credentials.json")
# Create a bucket object for our bucket
bucket = storage_client.get_bucket("automato-bucket")
# Create a blob object from the filepath
folder_name = 'features/binance_features'
prefix = folder_name + '/' if folder_name else None
blobs = bucket.list_blobs(prefix=prefix)

for i, blob in enumerate(blobs):
    if blob.name[-1] != '/':
        blob = bucket.blob(blob.name)
        byte_buffer = io.BytesIO()
        blob.download_to_file(byte_buffer)
        byte_buffer.seek(0)
        file_content = byte_buffer.getvalue().decode('utf-8')
        df = pd.read_csv(io.StringIO(file_content))
        upload_to_postgres(df, 'binance_features', new_table=True if i == 1 else False)

print('GCS data was transferred to PostgreSQL database.')
