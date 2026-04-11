# --- S3 Buckets (one per project) ---
resource "aws_s3_bucket" "abac" {
  for_each      = var.projects
  bucket        = "abac-${each.key}-${local.suffix}"
  force_destroy = true
  tags          = { project = each.value }
}

# --- Bucket policy: Deny layer (ABAC enforcement) ---
resource "aws_s3_bucket_policy" "abac" {
  for_each = var.projects
  bucket   = aws_s3_bucket.abac[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyUnlessProjectTagMatches"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.abac[each.key].arn,
          "${aws_s3_bucket.abac[each.key].arn}/*"
        ]
        Condition = {
          StringNotEquals = {
            "aws:PrincipalTag/project" = each.value
          }
          Null = {
            "aws:PrincipalTag/project" = "false"
          }
          ArnNotLike = {
            "aws:PrincipalArn" = "arn:aws:iam::${local.account_id}:root"
          }
        }
      }
    ]
  })
}
