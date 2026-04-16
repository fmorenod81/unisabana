output "api_endpoint" {
  value = "${aws_api_gateway_deployment.this.invoke_url}files"
}

output "s3_bucket" {
  value = aws_s3_bucket.this.id
}
