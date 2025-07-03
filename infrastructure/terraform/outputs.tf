output "s3_bucket_name" {
  value = aws_s3_bucket.frontend.bucket
}

output "rds_endpoint" {
  value = aws_db_instance.formdb.endpoint
}

output "db_name" {
  value = aws_db_instance.formdb.identifier
}

output "db_user" {
  value     = aws_db_instance.formdb.username
  sensitive = true
}

output "cloudfront_domain_name" {
  value = aws_cloudfront_distribution.frontend.domain_name
  description = "CloudFront distribution domain for the frontend."
}

output "api_gateway_endpoint" {
  value       = aws_apigatewayv2_api.api.api_endpoint
  description = "API Gateway endpoint URL."
}

output "lambda_function_name" {
  value       = aws_lambda_function.backend.function_name
  description = "Lambda function name."
}

output "iam_user_saisrigoutham_arn" {
  value = aws_iam_user.saisrigoutham.arn
}

output "iam_user_jerome_arn" {
  value = aws_iam_user.jerome.arn
}

output "saisrigoutham_temp_password" {
  value     = aws_iam_user_login_profile.saisrigoutham_login.encrypted_password
  sensitive = true
}

output "jerome_temp_password" {
  value     = aws_iam_user_login_profile.jerome_login.encrypted_password
  sensitive = true
} 