# CloudFront Module

This module creates a CloudFront distribution for serving a Single Page Application (SPA) from an S3 bucket with secure, opinionated defaults.

## Features

- CloudFront distribution with S3 origin
- Origin Access Control (OAC) for secure S3 access
- Security headers policy with HSTS, frame options, and content type options
- Custom error responses for SPA routing (404/403 → index.html)
- Origin Shield for improved performance and cost optimization (us-west-2)
- HTTPS redirect and TLS 1.2+ enforcement
- PriceClass_100 for cost optimization (US, Canada, Europe)

## Usage

```hcl
module "cloudfront" {
  source = "./modules/cloudfront"

  name_prefix                      = var.name_prefix
  suffix                          = var.suffix
  common_tags                     = var.common_tags
  environment                     = var.environment
  s3_bucket_name                  = module.s3.bucket_name
  s3_bucket_regional_domain_name  = module.s3.bucket_regional_domain_name
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| name_prefix | Prefix for resource names | `string` | n/a | yes |
| suffix | Suffix for resource names | `string` | n/a | yes |
| common_tags | Common tags to apply to all resources | `map(string)` | n/a | yes |
| s3_bucket_name | Name of the S3 bucket for the SPA website | `string` | n/a | yes |
| s3_bucket_regional_domain_name | Regional domain name of the S3 bucket | `string` | n/a | yes |
| environment | Environment name for the comment | `string` | `"dev"` | no |

## Outputs

| Name | Description |
|------|-------------|
| cloudfront_distribution_id | ID of the CloudFront distribution |
| cloudfront_distribution_arn | ARN of the CloudFront distribution |
| cloudfront_domain_name | Domain name of the CloudFront distribution |
| spa_website_url | URL of the SPA website |
| origin_access_control_id | ID of the CloudFront Origin Access Control |
| response_headers_policy_id | ID of the CloudFront Response Headers Policy |

## Opinionated Defaults

This module uses secure, cost-effective defaults:

- **Price Class**: PriceClass_100 (US, Canada, Europe only)
- **Origin Shield**: Enabled in us-west-2 region
- **TLS Version**: Minimum TLSv1.2_2021
- **Root Object**: index.html
- **Caching**: Optimized for static websites (3600s default TTL)
- **Security**: Comprehensive security headers enabled

## Security Features

- **Origin Access Control (OAC)**: Secures access to S3 bucket using AWS Signature Version 4
- **Security Headers**: Implements HSTS, frame options, content type options, and referrer policy
- **HTTPS Enforcement**: Redirects all HTTP traffic to HTTPS
- **TLS 1.2+**: Enforces minimum TLS version for secure connections

## SPA Support

The module includes custom error responses that redirect 403 and 404 errors to `/index.html`, enabling proper client-side routing for Single Page Applications.
