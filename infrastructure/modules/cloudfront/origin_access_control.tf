########################################################
# CloudFront Origin Access Control
########################################################

resource "aws_cloudfront_origin_access_control" "spa_website" {
  name                              = "${var.name_prefix}spa-website-oac-${var.suffix}"
  description                       = "OAC for SPA website S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
