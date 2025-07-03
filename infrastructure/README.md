# Infrastructure

This directory contains Terraform code for AWS infrastructure provisioning. 

## Lambda Build Requirement for Terraform

Before running `terraform validate` or `terraform plan`, you must ensure the Lambda zip file exists. Otherwise, Terraform will fail with a file not found error for the Lambda zip.

You can do this by running:

```sh
cd ../backend
bash build_lambda.sh
cd ../infrastructure/terraform
```

Or, if you want to create a dummy file for validation only:

```sh
touch ../../backend/backend-lambda.zip
```

### Makefile Target (Optional)

Add this to your Makefile for convenience:

```makefile
validate:
	cd backend && bash build_lambda.sh
	cd infrastructure/terraform && terraform validate
```

Now you can simply run:

```sh
make validate
``` 