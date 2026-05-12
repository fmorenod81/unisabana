variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "keypair_name" {
  description = "Name of the EC2 key pair"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "environment_tag" {
  description = "Environment tag"
  type        = string
  default     = "development"
}

variable "web_vpc_cidr" {
  description = "CIDR block for the web VPC"
  type        = string
  default     = "10.10.0.0/16"
}

variable "app_vpc_cidr" {
  description = "CIDR block for the app VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "web_public_subnet1_cidr" {
  description = "CIDR block for web public subnet 1"
  type        = string
  default     = "10.10.1.0/24"
}

variable "web_public_subnet2_cidr" {
  description = "CIDR block for web public subnet 2"
  type        = string
  default     = "10.10.2.0/24"
}

variable "app_private_subnet1_cidr" {
  description = "CIDR block for app private subnet 1"
  type        = string
  default     = "10.20.1.0/24"
}

variable "app_private_subnet2_cidr" {
  description = "CIDR block for app private subnet 2"
  type        = string
  default     = "10.20.2.0/24"
}

variable "app_public_subnet_cidr" {
  description = "CIDR block for app public NAT subnet"
  type        = string
  default     = "10.20.3.0/24"
}
