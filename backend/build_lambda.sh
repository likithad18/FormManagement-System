#!/bin/bash
set -e
cd "$(dirname "$0")"
rm -rf package backend-lambda.zip
mkdir package
pip install -r requirements.txt -t package/
cp -r src/* package/
cd package
zip -r ../backend-lambda.zip .
cd ..
echo "Lambda package created: backend-lambda.zip" 