"""
Task Processor Lambda Function
Processes tasks from SQS queue and updates status in DynamoDB
"""
import json
import time
import boto3
from datetime import datetime
import os
from PIL import Image
import io

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')

table_name = os.environ.get('DYNAMODB_TABLE', 'task-status')
input_bucket = os.environ.get('INPUT_BUCKET')
output_bucket = os.environ.get('OUTPUT_BUCKET')

table = dynamodb.Table(table_name)

def update_task_status(task_id, status, result=None, error=None):
    """Update task status in DynamoDB"""
    item = {
        'taskId': task_id,
        'status': status,
        'updatedAt': datetime.utcnow().isoformat(),
        'timestamp': int(time.time())
    }
    
    if result:
        item['result'] = result
    if error:
        item['error'] = error
    
    table.put_item(Item=item)
    print(f"Updated task {task_id} status to {status}")

# def process_image_task(data):
#     """Resize an image from S3"""
#     print(f"Processing image resize: {data}")
    
#     # Parse input data
#     if isinstance(data, str):
#         # Simple format: just filename
#         source_key = data
#         target_size = (800, 600)
#     else:
#         # Advanced format: {"key": "photo.jpg", "width": 800, "height": 600}
#         source_key = data.get('key', data.get('filename'))
#         target_size = (
#             data.get('width', 800),
#             data.get('height', 600)
#         )
    
#     try:
#         # Download image from S3
#         print(f"Downloading {source_key} from {input_bucket}")
#         response = s3.get_object(Bucket=input_bucket, Key=source_key)
#         image_content = response['Body'].read()
        
#         # Open image with Pillow
#         image = Image.open(io.BytesIO(image_content))
#         print(f"Original size: {image.size}")
        
#         # Resize image
#         resized_image = image.resize(target_size, Image.Resampling.LANCZOS)
#         print(f"Resized to: {resized_image.size}")
        
#         # Save to bytes
#         output_buffer = io.BytesIO()
#         format = image.format if image.format else 'JPEG'
#         resized_image.save(output_buffer, format=format)
#         output_buffer.seek(0)
        
#         # Generate output filename
#         base_name = os.path.splitext(source_key)[0]
#         extension = os.path.splitext(source_key)[1]
#         output_key = f"{base_name}_resized_{target_size[0]}x{target_size[1]}{extension}"
        
#         # Upload to output bucket
#         print(f"Uploading to {output_bucket}/{output_key}")
#         s3.put_object(
#             Bucket=output_bucket,
#             Key=output_key,
#             Body=output_buffer.getvalue(),
#             ContentType=f'image/{format.lower()}'
#         )
        
#         # Generate presigned URL
#         presigned_url = s3.generate_presigned_url(
#             'get_object',
#             Params={'Bucket': output_bucket, 'Key': output_key},
#             ExpiresIn=604800  # 7 days
#         )
        
#         return {
#             "status": "success",
#             "message": f"Image resized successfully",
#             "original_size": f"{image.size[0]}x{image.size[1]}",
#             "new_size": f"{target_size[0]}x{target_size[1]}",
#             "output_key": output_key,
#             "output_url": presigned_url
#         }
        
#     except Exception as e:
#         print(f"Error processing image: {str(e)}")
#         raise

def process_image_task(data):
    """Copy image between buckets"""
    print(f"Processing image: {data}")
    
    source_key = data if isinstance(data, str) else data.get('key')
    
    try:
        # Copy from input to output bucket
        output_key = f"processed_{source_key}"
        
        s3.copy_object(
            CopySource={'Bucket': input_bucket, 'Key': source_key},
            Bucket=output_bucket,
            Key=output_key
        )
        
        return {
            "status": "success",
            "message": "Image processed",
            "output_key": output_key
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

def process_email_task(data):
    """Process email sending task"""
    print(f"Sending email to: {data}")
    time.sleep(0.5)  # Simulate processing
    return {"status": "success", "message": "Email sent successfully", "recipient": data}

def process_data_task(data):
    """Process data transformation task"""
    print(f"Processing data: {data}")
    time.sleep(2)  # Simulate processing
    records = data.get('records', 0) if isinstance(data, dict) else 0
    return {"status": "success", "message": "Data processed", "records_processed": records}

def lambda_handler(event, context):
    """Main Lambda handler"""
    for record in event['Records']:
        try:
            # Parse message
            message_body = json.loads(record['body'])
            task_id = message_body['task_id']
            task_type = message_body['type']
            task_data = message_body['data']
            
            print(f"Processing {task_type} task: {task_id}")
            
            # Update status to PROCESSING
            update_task_status(task_id, 'PROCESSING', {'type': task_type})
            
            # Route to appropriate processor
            if task_type == 'IMAGE_RESIZE':
                result = process_image_task(task_data)
            elif task_type == 'SEND_EMAIL':
                result = process_email_task(task_data)
            elif task_type == 'PROCESS_DATA':
                result = process_data_task(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Update status to COMPLETED
            update_task_status(task_id, 'COMPLETED', result)
            print(f"Task {task_id} completed successfully")
            
        except Exception as e:
            # Update status to FAILED
            error_msg = str(e)
            update_task_status(task_id, 'FAILED', error=error_msg)
            print(f"Task {task_id} failed: {error_msg}")
            raise  # Let Lambda handle retry
    
    return {'statusCode': 200, 'body': json.dumps('Tasks processed successfully')}