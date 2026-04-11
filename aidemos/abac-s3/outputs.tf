output "user_credentials" {
  description = "Access keys for each ABAC user"
  value = {
    for k, v in var.projects : k => {
      profile    = "abac-${k}"
      access_key = aws_iam_access_key.abac[k].id
      secret_key = nonsensitive(aws_iam_access_key.abac[k].secret)
    }
  }
  #sensitive = true
  
}

output "bucket_names" {
  description = "Bucket names per project"
  value       = { for k, v in var.projects : k => aws_s3_bucket.abac[k].id }
}
