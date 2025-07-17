terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region for resources"
  default     = "us-east-2"
}

variable "environment" {
  description = "Environment name"
  default     = "dev"
}

# SQS Queue
resource "aws_sqs_queue" "task_queue" {
  name                      = "${var.environment}-task-queue"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600  # 4 days
  receive_wait_time_seconds = 20      # Long polling
  visibility_timeout_seconds = 300    # 5 minutes

  tags = {
    Environment = var.environment
    Project     = "distributed-task-queue"
  }
}

# DynamoDB Table
resource "aws_dynamodb_table" "task_status" {
  name           = "${var.environment}-task-status"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "taskId"

  attribute {
    name = "taskId"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = false
  }

  tags = {
    Environment = var.environment
    Project     = "distributed-task-queue"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.environment}-task-processor-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.environment}-task-processor-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.task_queue.arn
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.task_status.arn
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "task_processor" {
  filename         = "../lambda/task_processor.zip"
  function_name    = "${var.environment}-task-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "task_processor.lambda_handler"
  source_code_hash = filebase64sha256("../lambda/task_processor.zip")
  runtime         = "python3.11"
  timeout         = 300

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.task_status.name
      ENVIRONMENT    = var.environment
    }
  }

  tags = {
    Environment = var.environment
    Project     = "distributed-task-queue"
  }
}

# SQS Lambda Trigger
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.task_queue.arn
  function_name    = aws_lambda_function.task_processor.arn
  batch_size       = 10
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.task_processor.function_name}"
  retention_in_days = 7
}

# Outputs
output "queue_url" {
  description = "URL of the SQS queue"
  value       = aws_sqs_queue.task_queue.url
}

output "dynamodb_table" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.task_status.name
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.task_processor.function_name
}