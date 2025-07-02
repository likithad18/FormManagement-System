# Only create the S3 bucket policy if public policies are allowed. If Block Public Access is enabled, skip this resource.
# You can use a variable or comment out this resource if you want to skip it entirely.
# To skip, comment out the following resource block:
# resource "aws_s3_bucket_policy" "frontend_policy" {
#   bucket = aws_s3_bucket.frontend.id
#   policy = data.aws_iam_policy_document.s3_policy.json
# }

resource "aws_s3_bucket_policy" "frontend_policy" {
  count  = var.enable_s3_public_policy ? 1 : 0
  bucket = aws_s3_bucket.frontend.id
  policy = data.aws_iam_policy_document.s3_policy.json
}

variable "enable_s3_public_policy" {
  description = "Set to true to enable S3 public bucket policy. Set to false to skip if Block Public Access is enabled."
  type        = bool
  default     = false
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.frontend.arn}/*"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    effect = "Allow"
  }
}

resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "frontendS3Origin"
  }
  enabled             = true
  default_root_object = "index.html"
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "frontendS3Origin"
    viewer_protocol_policy = "redirect-to-https"
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
} 