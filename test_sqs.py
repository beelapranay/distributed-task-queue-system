import boto3
import json

# Create SQS client
sqs = boto3.client('sqs', region_name='us-east-2')

# Queue URL (find this in SQS console - click on your queue)
QUEUE_URL = 'https://sqs.us-east-2.amazonaws.com/398028532400/first-queue'

# Send a message
def send_task():
    message = {
        'task_id': '123',
        'type': 'HELLO_WORLD',
        'data': 'This is my first task!'
    }
    
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message)
    )
    
    print(f"Message sent! ID: {response['MessageId']}")

def receive_task():
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1
    )
    
    messages = response.get('Messages', [])
    if messages:
        message = messages[0]
        body = json.loads(message['Body'])
        print(f"Received task: {body}")
        
        # Delete message after processing
        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=message['ReceiptHandle']
        )
        print("Message deleted from queue")
    else:
        print("No messages in queue")

if __name__ == '__main__':
    send_task()
    #receive_task()

