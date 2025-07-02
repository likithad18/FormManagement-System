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

# S3 bucket for frontend static hosting
resource "aws_s3_bucket" "frontend" {
  bucket = var.s3_bucket_name
  force_destroy = true
}

# PostgreSQL RDS instance
resource "aws_db_instance" "formdb" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro"
  name                 = var.db_name
  username             = var.db_user
  password             = var.db_password
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
  publicly_accessible  = false
}

# Lambda, API Gateway, IAM, etc. to be added 