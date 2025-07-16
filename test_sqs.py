import boto3
import json
import sys

sqs = boto3.client('sqs', region_name='us-east-2')
QUEUE_URL = 'https://sqs.us-east-2.amazonaws.com/398028532400/first-queue'

def send_task(task_type, task_data):
    message = {
        'task_id': f'{task_type}-{123}',
        'type': task_type,
        'data': task_data
    }
    
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message)
    )
    
    print(f"Sent {task_type} task! ID: {response['MessageId']}")

if __name__ == '__main__':
    # Send different task types
    send_task('IMAGE_RESIZE', 'profile_pic.jpg')
    send_task('SEND_EMAIL', 'user@example.com')
    send_task('PROCESS_DATA', {'records': 1000})
    send_task('UNKNOWN_TYPE', 'This should fail gracefully')