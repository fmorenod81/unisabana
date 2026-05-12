terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "keypair_name" {
  description = "Name of the EC2 Key Pair"
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

locals {
  user_data = base64encode(<<-EOF
              #!/bin/bash
              set -e

              yum update -y
              yum install -y docker
              systemctl enable --now docker

              docker run hello-world || true
              docker run -d -p 80:80 benpiper/mtwa:web || true
              EOF
  )
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "vpc-main"
    Environment = var.environment_tag
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name        = "pbsn1"
    Environment = var.environment_tag
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "igw-main"
    Environment = var.environment_tag
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "rt-public"
    Environment = var.environment_tag
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "main" {
  name_prefix = "main-"
  description = "Security group for EC2 instance"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name        = "sg-main"
    Environment = var.environment_tag
  }
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.main.id
  description       = "Allow HTTP"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.main.id
  description       = "Allow HTTPS"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.main.id
  description       = "Allow SSH"
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.main.id
  description       = "Allow all outbound traffic"
  from_port         = -1
  to_port           = -1
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_network_interface" "main" {
  subnet_id       = aws_subnet.public.id
  security_groups = [aws_security_group.main.id]

  tags = {
    Name        = "eni-main"
    Environment = var.environment_tag
  }
}

resource "aws_eip" "main" {
  domain            = "vpc"
  network_interface = aws_network_interface.main.id
  depends_on        = [aws_internet_gateway.main]

  tags = {
    Name        = "eip-main"
    Environment = var.environment_tag
  }
}

resource "aws_instance" "main" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.keypair_name
  user_data     = local.user_data

  network_interface {
    network_interface_id = aws_network_interface.main.id
    device_index         = 0
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
  }

  tags = {
    Name        = "ec2-instance"
    Environment = var.environment_tag
  }

  depends_on = [aws_route_table_association.public, aws_internet_gateway.main]
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

output "elastic_ip" {
  description = "Elastic IP address assigned to the instance"
  value       = aws_eip.main.public_ip
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.main.id
}

output "ssh_connection" {
  description = "SSH connection string"
  value       = "ssh -i /path/to/keypair.pem ec2-user@${aws_eip.main.public_ip}"
}

output "http_endpoint" {
  description = "HTTP endpoint"
  value       = "http://${aws_eip.main.public_ip}"
}

output "https_endpoint" {
  description = "HTTPS endpoint"
  value       = "https://${aws_eip.main.public_ip}"
}
