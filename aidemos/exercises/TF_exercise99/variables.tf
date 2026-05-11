variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "key_pair_name" {
  description = "Name of the existing EC2 key pair"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance size for both public and private instances"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}
