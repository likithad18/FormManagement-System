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
  lifecycle {
    prevent_destroy = false
    ignore_changes  = [name]
  }
}

resource "aws_lambda_function" "backend" {
  function_name = "form-backend-api"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "src.main.handler"
  runtime       = "python3.10"
  filename      = "../../backend/backend-lambda.zip"
  source_code_hash = filebase64sha256("../../backend/backend-lambda.zip")
  timeout       = 30
  environment {
    variables = {
      DATABASE = var.db_url
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
  tags = {
    Email = "saisrigoutham.gadi@cyndx.com"
  }
}

resource "aws_iam_user" "jerome" {
  name = "jerome.caisip-ext"
  tags = {
    Email = "jerome.caisip-ext@cyndx.com"
  }
}

resource "aws_iam_user_login_profile" "saisrigoutham_login" {
  user                    = aws_iam_user.saisrigoutham.name
  password_length         = 20
  password_reset_required = true
}

resource "aws_iam_user_login_profile" "jerome_login" {
  user                    = aws_iam_user.jerome.name
  password_length         = 20
  password_reset_required = true
}

resource "aws_iam_policy" "read_only_monitoring" {
  name        = "ReadOnlyMonitoringAccess"
  description = "Provides read-only access to CloudWatch, Lambda, RDS, S3, and API Gateway"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:Describe*",
          "cloudwatch:Get*",
          "cloudwatch:List*",
          "logs:Describe*",
          "logs:Get*",
          "logs:List*",
          "logs:StartLiveTail",
          "logs:TestMetricFilter",
          "lambda:Get*",
          "lambda:List*",
          "lambda:Describe*",
          "rds:Describe*",
          "rds:List*",
          "s3:Get*",
          "s3:List*",
          "apigateway:GET"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "saisrigoutham_attach" {
  user       = aws_iam_user.saisrigoutham.name
  policy_arn = aws_iam_policy.read_only_monitoring.arn
}

resource "aws_iam_user_policy_attachment" "jerome_attach" {
  user       = aws_iam_user.jerome.name
  policy_arn = aws_iam_policy.read_only_monitoring.arn
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

# If your secret is created outside this workspace, use a data source:
# data "aws_secretsmanager_secret" "db_credentials" {
#   name = "form-db-credentials"
# }
# And reference:
# Resource = data.aws_secretsmanager_secret.db_credentials.arn 