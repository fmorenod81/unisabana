# --- IAM Users (one per project) ---
resource "aws_iam_user" "abac" {
  for_each      = var.projects
  name          = "abac-${each.key}-${local.suffix}"
  force_destroy = true
  tags          = { project = each.value }
}

resource "aws_iam_access_key" "abac" {
  for_each = var.projects
  user     = aws_iam_user.abac[each.key].name
}

# --- Identity policy: broad Allow on ALL demo buckets ---
resource "aws_iam_user_policy" "abac_s3" {
  for_each = var.projects
  name     = "abac-s3-access"
  user     = aws_iam_user.abac[each.key].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "AllowS3OnDemoBuckets"
        Effect   = "Allow"
        Action   = "s3:*"
        Resource = flatten([
          for p in keys(var.projects) : [
            aws_s3_bucket.abac[p].arn,
            "${aws_s3_bucket.abac[p].arn}/*"
          ]
        ])
      }
    ]
  })
}
