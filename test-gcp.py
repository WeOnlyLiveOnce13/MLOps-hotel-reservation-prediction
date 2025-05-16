from google.cloud import storage

# Initialize the client - this will use your environment variable
storage_client = storage.Client()

# List buckets (if you have permission)
buckets = list(storage_client.list_buckets())
print(f"Found {len(buckets)} buckets:")
for bucket in buckets:
    print(bucket.name)