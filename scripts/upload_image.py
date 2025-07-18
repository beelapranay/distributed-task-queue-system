import boto3
import sys
from config import AWS_REGION

s3 = boto3.client('s3', region_name=AWS_REGION)

INPUT_BUCKET = 'dev-task-queue-input-398028532400'

def upload_image(file_path):
    key = file_path.split('/')[-1]  # Just filename
    
    print(f"Uploading {file_path} to s3://{INPUT_BUCKET}/{key}")
    s3.upload_file(file_path, INPUT_BUCKET, key)
    print(f"✓ Uploaded successfully!")
    return key

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python upload_image.py <image_path>")
        sys.exit(1)
    
    upload_image(sys.argv[1])