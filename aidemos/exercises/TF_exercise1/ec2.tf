terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "key_name" {
  description = "Name of the existing EC2 KeyPair to enable SSH access"
  type        = string
}

variable "ubuntu_distribution" {
  description = "Ubuntu distribution codename (e.g. noble, jammy, focal, bionic)"
  type        = string
  default     = "noble"
}

locals {
  ubuntu_ssm_parameters = {
    noble  = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
    jammy  = "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id"
    focal  = "/aws/service/canonical/ubuntu/server/20.04/stable/current/amd64/hvm/ebs-gp2/ami-id"
    bionic = "/aws/service/canonical/ubuntu/server/18.04/stable/current/amd64/hvm/ebs-gp2/ami-id"
  }
}

data "aws_ssm_parameter" "ubuntu" {
  name = local.ubuntu_ssm_parameters[var.ubuntu_distribution]
}

resource "aws_instance" "ubuntu" {
  ami           = data.aws_ssm_parameter.ubuntu.value
  instance_type = "t3.micro"
  key_name      = var.key_name

  tags = {
    Name = "ubuntu-${var.ubuntu_distribution}-instance"
  }
}

output "instance_id" {
  value = aws_instance.ubuntu.id
}

output "public_ip" {
  value = aws_instance.ubuntu.public_ip
}
