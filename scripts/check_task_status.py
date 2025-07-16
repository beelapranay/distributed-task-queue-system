"""
Check task status from DynamoDB
"""
import boto3
import argparse
from datetime import datetime
from config import AWS_REGION, TABLE_NAME

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)

def get_task_status(task_id):
    """Get status of a specific task"""
    try:
        response = table.get_item(Key={'taskId': task_id})
        
        if 'Item' in response:
            task = response['Item']
            print(f"\nTask ID: {task['taskId']}")
            print(f"Status: {task['status']}")
            print(f"Updated: {task['updatedAt']}")
            
            if 'result' in task:
                print(f"Result: {task['result']}")
            if 'error' in task:
                print(f"Error: {task['error']}")
        else:
            print(f"Task {task_id} not found")
    except Exception as e:
        print(f"Error checking task status: {e}")

def list_recent_tasks(limit=10):
    """List recent tasks"""
    try:
        response = table.scan(Limit=limit)
        tasks = response['Items']
        
        # Sort by timestamp
        tasks.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        print(f"\nRecent Tasks (showing {len(tasks)}):")
        print("-" * 60)
        
        for task in tasks:
            status_emoji = {
                'COMPLETED': '✓',
                'PROCESSING': '⟳',
                'FAILED': '✗'
            }.get(task['status'], '?')
            
            print(f"{status_emoji} {task['taskId']:<30} {task['status']:<12} {task['updatedAt']}")
    except Exception as e:
        print(f"Error listing tasks: {e}")

def main():
    parser = argparse.ArgumentParser(description='Check task status')
    parser.add_argument('--task-id', help='Specific task ID to check')
    parser.add_argument('--list', action='store_true', help='List recent tasks')
    parser.add_argument('--limit', type=int, default=10, help='Number of tasks to list')
    
    args = parser.parse_args()
    
    if args.task_id:
        get_task_status(args.task_id)
    elif args.list:
        list_recent_tasks(args.limit)
    else:
        list_recent_tasks(5)

if __name__ == '__main__':
    main()