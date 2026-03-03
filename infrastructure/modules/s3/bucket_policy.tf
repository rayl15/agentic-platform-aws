########################################################
# S3 Bucket Policy for CloudFront OAC Access
########################################################

data "aws_iam_policy_document" "cloudfront_oac" {
  count = var.enable_cloudfront_oac_policy ? 1 : 0

  statement {
    sid    = "AllowCloudFrontServicePrincipal"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.this.arn}/*"
    ]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [var.cloudfront_distribution_arn]
    }
  }
}

########################################################
# S3 Bucket Policy
########################################################

resource "aws_s3_bucket_policy" "this" {
  count = var.enable_bucket_policy || var.enable_cloudfront_oac_policy ? 1 : 0

  bucket = aws_s3_bucket.this.id
  policy = var.enable_cloudfront_oac_policy ? data.aws_iam_policy_document.cloudfront_oac[0].json : var.bucket_policy_json
}
