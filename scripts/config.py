"""
Configuration for the task queue system
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-2')
QUEUE_URL = os.environ.get('QUEUE_URL', '')
TABLE_NAME = os.environ.get('DYNAMO_TABLE', 'task-status')

# Validate required config
if not QUEUE_URL:
    raise ValueError(
        "QUEUE_URL environment variable must be set. "
        "Copy .env.example to .env and update with your values."
    )