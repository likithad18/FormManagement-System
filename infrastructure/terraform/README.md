# Terraform AWS Infrastructure

This directory contains Terraform code to provision AWS resources for the Form Management System.

## Resources
- S3 bucket for frontend static hosting
- RDS PostgreSQL instance for backend
- (To be added: Lambda, API Gateway, IAM roles)

## Usage

1. Install [Terraform](https://www.terraform.io/downloads.html)
2. Configure your AWS credentials (e.g., with `aws configure`)
3. Set required variables (see `variables.tf`). You can use a `terraform.tfvars` file:
   ```hcl
   s3_bucket_name = "your-unique-bucket-name"
   db_password    = "your-secure-password"
   ```
4. Initialize and apply:
   ```bash
   terraform init
   terraform apply
   ```

## Outputs
- S3 bucket name
- RDS endpoint, DB name, and user 