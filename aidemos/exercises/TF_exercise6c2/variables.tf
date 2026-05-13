variable "region" {
  default = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "vpcn_cidr" {
  description = "CIDR block for vpcn (Web VPC)"
  default     = "10.10.0.0/16"
}

variable "vpcp_cidr" {
  description = "CIDR block for vpcp (App VPC)"
  default     = "10.20.0.0/16"
}

variable "keypair_name" {
  description = "Name of the existing EC2 KeyPair"
  type        = string
}