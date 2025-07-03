#!/bin/bash
set -e

echo "Cleaning previous build..."
rm -rf package backend-lambda.zip

echo "Creating package directory..."
mkdir package

echo "Installing Python dependencies..."
# Force pip to use manylinux wheels compatible with Amazon Linux 2
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt -t package/ \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --implementation cp \
  --python-version 3.10 \
  --abi cp310

echo "Copying application code..."
# Keep src folder so relative imports work
cp -r src package/

# Make sure it's a package
mkdir -p package/src
touch package/src/__init__.py

echo "Zipping Lambda package..."
cd package
zip -r ../backend-lambda.zip .
cd ..

echo "✅ Lambda package created: backend-lambda.zip" 