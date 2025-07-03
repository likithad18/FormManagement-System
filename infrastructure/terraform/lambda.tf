resource "aws_iam_role" "lambda_exec" {
  name = "form_backend_lambda_exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_cloudwatch_log_group" "lambda_backend" {
  name              = "/aws/lambda/${aws_lambda_function.backend.function_name}"
  retention_in_days = 3
}

resource "aws_lambda_function" "backend" {
  function_name = "form-backend-api"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "main.handler" # To be updated with actual handler
  runtime       = "python3.11"
  filename      = "../../backend/backend-lambda.zip"
  source_code_hash = filebase64sha256("../../backend/backend-lambda.zip")
  timeout       = 30
  environment {
    variables = {
      DATABASE_URL = var.db_url
      SECRETS_MANAGER_ARN = aws_secretsmanager_secret.db_credentials.arn
    }
  }
  depends_on = [null_resource.build_lambda]
}

# API Gateway HTTP API
resource "aws_apigatewayv2_api" "api" {
  name          = "form-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.backend.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.backend.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

resource "aws_iam_user" "saisrigoutham" {
  name = "saisrigoutham.gadi"
}

resource "aws_iam_user" "jerome" {
  name = "jerome.caisip-ext"
}

resource "aws_iam_policy" "readonly_access" {
  name        = "FormAppReadOnlyAccess"
  description = "Read-only access to CloudWatch, Lambda, RDS, S3, and API Gateway."
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "cloudwatch:Describe*",
          "cloudwatch:Get*",
          "cloudwatch:List*",
          "logs:Describe*",
          "logs:Get*",
          "logs:List*",
          "lambda:List*",
          "lambda:Get*",
          "rds:Describe*",
          "rds:List*",
          "s3:Get*",
          "s3:List*",
          "apigateway:GET",
          "apigateway:GET*",
          "apigateway:Describe*"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "saisrigoutham_readonly" {
  user       = aws_iam_user.saisrigoutham.name
  policy_arn = aws_iam_policy.readonly_access.arn
}

resource "aws_iam_user_policy_attachment" "jerome_readonly" {
  user       = aws_iam_user.jerome.name
  policy_arn = aws_iam_policy.readonly_access.arn
}

resource "aws_iam_policy" "lambda_secrets_access" {
  name        = "LambdaSecretsManagerAccess"
  description = "Allow Lambda to get secret value for DB credentials."
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["secretsmanager:GetSecretValue"],
        Resource = aws_secretsmanager_secret.db_credentials.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_secrets_access" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_secrets_access.arn
} 