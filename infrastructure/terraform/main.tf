terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "aws" {
  region = var.aws_region
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "FormManagement-System"
}

variable "environment" {
  description = "Environment (dev, prod, etc.) for tagging"
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Owner for tagging"
  type        = string
  default     = "likithad18"
}

# =============================
# S3 Bucket for Frontend Hosting (5GB free tier)
# =============================
resource "aws_s3_bucket" "frontend" {
  bucket        = var.s3_bucket_name
  force_destroy = true
  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
  }
}

# NOTE: Store DB credentials in AWS Secrets Manager and reference them in Lambda and RDS resources for secure access.
# Example (not implemented here):
# resource "aws_secretsmanager_secret" "db_credentials" { ... }
# resource "aws_secretsmanager_secret_version" "db_credentials_version" { ... }
# Then reference secret in Lambda and RDS environment/parameter.

resource "aws_secretsmanager_secret" "db_credentials" {
  name = "formdb-credentials"
  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials_version" {
  secret_id     = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_user,
    password = var.db_password
  })
}

# =============================
# RDS PostgreSQL Instance (t3.micro or t4g.micro for dev, free tier eligible)
# =============================
resource "aws_db_instance" "formdb" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15.10"
  instance_class       = var.rds_instance_class # t3.micro or t4g.micro for dev
  identifier           = var.db_name
  username             = jsondecode(aws_secretsmanager_secret_version.db_credentials_version.secret_string)["username"]
  password             = jsondecode(aws_secretsmanager_secret_version.db_credentials_version.secret_string)["password"]
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
  publicly_accessible  = false
  vpc_security_group_ids = [aws_security_group.rds.id]
  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
  }
}
# For production, consider Aurora Serverless for variable workloads.

resource "aws_security_group" "rds" {
  name        = "formdb-sg"
  description = "Allow access to RDS only from Lambda"
  vpc_id      = var.vpc_id
  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
  }

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "lambda" {
  name        = "lambda-sg"
  description = "Lambda security group"
  vpc_id      = var.vpc_id
  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
  }
}

# Lambda, API Gateway, IAM, etc. to be added 

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "FormAppDashboard"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        x = 0
        y = 0
        width = 12
        height = 6
        properties = {
          metrics = [
            [ "AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.backend.function_name ],
            [ ".", "Invocations", ".", "." ]
          ]
          period = 300
          stat = "Sum"
          region = var.aws_region
          title = "Lambda Errors & Invocations"
        }
      }
    ]
  })
}

resource "aws_sns_topic" "alerts" {
  name = "formapp-alerts"
  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "LambdaErrorAlarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alarm if Lambda errors > 0"
  dimensions = {
    FunctionName = aws_lambda_function.backend.function_name
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
  }
}

resource "aws_s3_bucket_policy" "frontend_public_read" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "arn:aws:s3:::${aws_s3_bucket.frontend.id}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.frontend]
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
} 