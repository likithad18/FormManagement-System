output "s3_bucket_name" {
  value = aws_s3_bucket.frontend.bucket
}

output "rds_endpoint" {
  value = aws_db_instance.formdb.endpoint
}

output "db_name" {
  value = aws_db_instance.formdb.name
}

output "db_user" {
  value = aws_db_instance.formdb.username
}

output "cloudfront_domain_name" {
  value = aws_cloudfront_distribution.frontend.domain_name
  description = "CloudFront distribution domain for the frontend."
} 