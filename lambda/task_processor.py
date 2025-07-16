"""
Task Processor Lambda Function
Processes tasks from SQS queue and updates status in DynamoDB
"""
import json
import time
import boto3
from datetime import datetime

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('task-status')

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

def process_image_task(data):
    """Process image resize task"""
    print(f"Resizing image: {data}")
    time.sleep(1)  # Simulate processing
    return {"status": "success", "message": "Image resized to 800x600", "file": data}

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