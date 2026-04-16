variable "s3_bucket_name" {
  description = "Name of the S3 bucket for file storage"
  type        = string
  default     = "lambda-apigw-demo-bucket"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}
