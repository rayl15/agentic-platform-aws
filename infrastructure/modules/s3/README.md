# S3 Bucket Module

A flexible and reusable Terraform module for creating S3 buckets with secure defaults and configurable features.

## Features

- **Always Secure**: Public access is always blocked (non-configurable for security)
- **Configurable Encryption**: Support for AES256 or KMS encryption
- **Versioning Control**: Enable/disable bucket versioning
- **Lifecycle Management**: Configurable lifecycle rules for object expiration and cleanup
- **CloudFront Integration**: Built-in support for CloudFront Origin Access Control (OAC)
- **Custom Policies**: Support for custom bucket policies
- **Flexible Tagging**: Customizable tags for resource management

## Usage Examples

### Basic S3 Bucket
```hcl
module "basic_bucket" {
  source = "./modules/s3"

  bucket_name  = "my-basic-bucket-12345"
  common_tags  = {
    Environment = "dev"
    Project     = "my-project"
  }
}
```

### S3 Bucket for Static Website with CloudFront
```hcl
module "spa_website_bucket" {
  source = "./modules/s3"

  bucket_name                    = "${local.name_prefix}spa-website-${local.suffix}"
  force_destroy                  = true
  bucket_type                    = "StaticWebsite"
  enable_cloudfront_oac_policy   = true
  cloudfront_distribution_arn    = module.cloudfront.cloudfront_distribution_arn
  
  enable_lifecycle_configuration = true
  lifecycle_rules = [
    {
      id                              = "spa_website_lifecycle"
      status                         = "Enabled"
      filter_prefix                  = ""
      abort_incomplete_multipart_days = 7
    }
  ]

  common_tags = local.common_tags
}
```

### S3 Bucket with KMS Encryption and Versioning
```hcl
module "secure_bucket" {
  source = "./modules/s3"

  bucket_name           = "my-secure-bucket-12345"
  versioning_enabled    = true
  encryption_algorithm  = "aws:kms"
  kms_key_id           = module.kms.kms_key_id
  
  enable_lifecycle_configuration = true
  lifecycle_rules = [
    {
      id                                = "cleanup_old_versions"
      status                           = "Enabled"
      noncurrent_version_expiration_days = 30
      abort_incomplete_multipart_days    = 1
    }
  ]

  common_tags = {
    Environment = "prod"
    Compliance  = "required"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| bucket_name | Name of the S3 bucket | `string` | n/a | yes |
| common_tags | Common tags to apply to all resources | `map(string)` | `{}` | no |
| force_destroy | Allow bucket to be destroyed even if it contains objects | `bool` | `false` | no |
| versioning_enabled | Enable versioning on the S3 bucket | `bool` | `false` | no |
| encryption_algorithm | Server-side encryption algorithm (AES256 or aws:kms) | `string` | `"AES256"` | no |
| kms_key_id | KMS key ID for encryption (required if encryption_algorithm is aws:kms) | `string` | `null` | no |
| enable_lifecycle_configuration | Enable lifecycle configuration for the bucket | `bool` | `false` | no |
| lifecycle_rules | List of lifecycle rules | `list(object)` | `[]` | no |
| enable_bucket_policy | Enable custom bucket policy | `bool` | `false` | no |
| bucket_policy_json | JSON policy document for the bucket | `string` | `null` | no |
| cloudfront_distribution_arn | CloudFront distribution ARN for OAC access | `string` | `null` | no |
| enable_cloudfront_oac_policy | Enable CloudFront Origin Access Control policy | `bool` | `false` | no |
| bucket_type | Type of bucket for tagging purposes | `string` | `"General"` | no |

### Lifecycle Rules Object Structure
```hcl
{
  id                                = string
  status                           = string           # "Enabled" or "Disabled"
  filter_prefix                    = optional(string, "")
  abort_incomplete_multipart_days  = optional(number, 7)
  expiration_days                  = optional(number)
  noncurrent_version_expiration_days = optional(number)
}
```

## Outputs

| Name | Description |
|------|-------------|
| bucket_name | Name of the S3 bucket |
| bucket_id | ID of the S3 bucket |
| bucket_arn | ARN of the S3 bucket |
| bucket_domain_name | Domain name of the S3 bucket |
| bucket_regional_domain_name | Regional domain name of the S3 bucket |
| bucket_hosted_zone_id | Hosted zone ID of the S3 bucket |
| bucket_region | Region of the S3 bucket |

## Security Features

- **Public Access Blocking**: All public access is always blocked (hardcoded for security)
- **Encryption**: Server-side encryption enabled by default (AES256)
- **KMS Support**: Optional KMS encryption with customer-managed keys
- **CloudFront OAC**: Built-in support for secure CloudFront access
- **Custom Policies**: Flexible policy attachment for specific access patterns

## Security Philosophy

This module prioritizes security by design:

- **No Public Access**: Public access blocking is hardcoded and cannot be disabled
- **Encryption by Default**: All buckets are encrypted at rest
- **Secure Access Patterns**: Supports CloudFront OAC and custom IAM policies only

## Best Practices

1. **Naming**: Use descriptive, unique bucket names with prefixes/suffixes
2. **Encryption**: Use KMS encryption for sensitive data
3. **Versioning**: Enable versioning for important data with lifecycle rules
4. **Lifecycle**: Configure lifecycle rules to manage costs and compliance
5. **Access**: Use least-privilege access policies (CloudFront OAC, IAM policies)
6. **Monitoring**: Add appropriate tags for cost allocation and monitoring
