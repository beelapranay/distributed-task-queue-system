"""
Submit tasks to the SQS queue
"""
import boto3
import json
import uuid
import argparse
from datetime import datetime
from config import AWS_REGION, QUEUE_URL

# Initialize SQS client
sqs = boto3.client('sqs', region_name=AWS_REGION)

def submit_task(task_type, task_data, priority='NORMAL'):
    """Submit a task to the queue"""
    task_id = f"{task_type}-{str(uuid.uuid4())[:8]}"
    
    message = {
        'task_id': task_id,
        'type': task_type,
        'data': task_data,
        'priority': priority
    }
    
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message)
    )
    
    print(f"✓ Submitted {task_type} task")
    print(f"  Task ID: {task_id}")
    print(f"  Message ID: {response['MessageId']}")
    
    return task_id

def main():
    parser = argparse.ArgumentParser(description='Submit tasks to the queue')
    parser.add_argument('--type', required=True, 
                      choices=['IMAGE_RESIZE', 'SEND_EMAIL', 'PROCESS_DATA'],
                      help='Type of task to submit')
    parser.add_argument('--data', required=True, help='Task data (JSON string or simple string)')
    parser.add_argument('--priority', default='NORMAL', choices=['LOW', 'NORMAL', 'HIGH'],
                      help='Task priority')
    
    args = parser.parse_args()
    
    # Try to parse data as JSON, otherwise use as string
    try:
        task_data = json.loads(args.data)
    except:
        task_data = args.data
    
    submit_task(args.type, task_data, args.priority)

if __name__ == '__main__':
    main()