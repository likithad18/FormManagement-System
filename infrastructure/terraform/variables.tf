variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for frontend hosting"
  type        = string
}

variable "db_name" {
  description = "Database name for RDS"
  type        = string
  default     = "formdb"
}

variable "db_user" {
  description = "Database username for RDS"
  type        = string
  default     = "formuser"
}

variable "db_password" {
  description = "Database password for RDS"
  type        = string
  sensitive   = true
}

variable "db_url" {
  description = "Database URL for Lambda environment"
  type        = string
  sensitive   = true
} 