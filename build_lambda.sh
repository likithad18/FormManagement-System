#!/bin/bash
set -e

# Clean previous builds
rm -rf package backend-lambda.zip
mkdir -p package

# Install dependencies
pip install -r requirements.txt -t package/

# Copy application code
cp -r src package/
cp main.py package/

# Remove unnecessary files
find package -name "*.pyc" -delete
find package -name "__pycache__" -delete

# Create zip archive
cd package
zip -r ../backend-lambda.zip .
cd ..

echo "Lambda package created: backend-lambda.zip" 