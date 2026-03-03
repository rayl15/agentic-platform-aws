########################################################
# CloudFront Outputs
########################################################

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.spa_website.id
}

output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.spa_website.arn
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.spa_website.domain_name
}

output "spa_website_url" {
  description = "URL of the SPA website"
  value       = "https://${aws_cloudfront_distribution.spa_website.domain_name}/frontend"
}

output "origin_access_control_id" {
  description = "ID of the CloudFront Origin Access Control"
  value       = aws_cloudfront_origin_access_control.spa_website.id
}

output "response_headers_policy_id" {
  description = "ID of the CloudFront Response Headers Policy"
  value       = aws_cloudfront_response_headers_policy.spa_website.id
}
