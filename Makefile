# Makefile for project automation

# Variables
FRONTEND_DIR=frontend
BACKEND_DIR=backend
S3_BUCKET=lalitha-terraform-20240703-unique
LAMBDA_ZIP=backend-lambda.zip

.PHONY: all frontend backend upload-frontend upload-backend clean validate plan apply set-api-base build-frontend-with-api deploy-all backend-test-cov

all: frontend backend

frontend:
	cd $(FRONTEND_DIR) && npm install && npm run build

upload-frontend:
	aws s3 cp $(FRONTEND_DIR)/dist/ s3://$(S3_BUCKET)/ --recursive

backend:
	cd $(BACKEND_DIR) && zip -r ../$(LAMBDA_ZIP) .

upload-backend:
	aws lambda update-function-code --function-name form-backend-api --zip-file fileb://$(LAMBDA_ZIP)

clean:
	rm -f $(LAMBDA_ZIP)

validate:
	cd backend && bash build_lambda.sh
	cd infrastructure/terraform && terraform validate

plan:
	cd backend && bash build_lambda.sh
	cd infrastructure/terraform && terraform plan

apply:
	cd backend && bash build_lambda.sh
	cd infrastructure/terraform && terraform apply

set-api-base:
	cd infrastructure/terraform && \
	API_URL=$$(terraform output -raw cloudfront_domain_name) && \
	echo "VITE_API_BASE=https://$${API_URL}" > ../../frontend/.env

build-frontend-with-api:
	make set-api-base
	cd frontend && npm install && npm run build

deploy-all:
	make build-frontend-with-api
	cd infrastructure/terraform && terraform apply -auto-approve

backend-test-cov:
	cd $(BACKEND_DIR) && pytest --cov=src tests 