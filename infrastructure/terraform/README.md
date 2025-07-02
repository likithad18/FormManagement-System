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

## IAM Collaborator Setup

This Terraform config creates IAM users for:
- saisrigoutham.gadi@cyndx.com
- jerome.caisip-ext@cyndx.com

Each user is granted read-only access to:
- CloudWatch logs and metrics
- Lambda function configurations
- RDS instance monitoring
- S3 bucket contents (read-only)
- API Gateway configurations

**To retrieve their credentials:**
- After `terraform apply`, go to the AWS IAM console, select the user, and create access keys (send securely to the user).
- Optionally, use Terraform output to display access key/secret (not recommended for production).

## Resource Tagging & Cost Tracking

All AWS resources are tagged with `Project`, `Environment`, and `Owner` for cost tracking and management. Use AWS Cost Explorer to filter by these tags and monitor usage. 