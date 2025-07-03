#!/bin/bash

# Set your local build directory and S3 bucket name
BUILD_DIR="build"
S3_BUCKET="lalitha-terraform-20240703-unique"

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
  echo "Directory $BUILD_DIR does not exist. Please build your site first."
  exit 1
fi

# Sync files to S3
echo "Uploading files from $BUILD_DIR to s3://$S3_BUCKET/ ..."
aws s3 cp "$BUILD_DIR/" "s3://$S3_BUCKET/" --recursive

echo "Upload complete!" 