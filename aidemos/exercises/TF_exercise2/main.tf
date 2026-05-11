variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "rhel_key_name" {
  description = "Name of the existing EC2 KeyPair for SSH access"
  type        = string
}

variable "ebs_size" {
  description = "Root EBS volume size for the EC2 instance, in GB"
  type        = number
}

variable "instance_size" {
  description = "Instance type (must be t3.medium, t2.medium, or t3.micro)"
  type        = string

  validation {
    condition     = contains(["t3.medium", "t2.medium", "t3.micro"], var.instance_size)
    error_message = "instance_size must be one of: t3.medium, t2.medium, t3.micro."
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "rhel8" {
  most_recent = true
  owners      = ["309956199498"] # Red Hat official

  filter {
    name   = "name"
    values = ["RHEL-8*_HVM-*-x86_64-*"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "rhel-vpc"
  }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "rhel-igw"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 0)
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "rhel-public-subnet"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = {
    Name = "rhel-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_instance" "rhel" {
  ami                         = data.aws_ami.rhel8.id
  instance_type               = var.instance_size
  key_name                    = var.rhel_key_name
  subnet_id                   = aws_subnet.public.id
  associate_public_ip_address = true

  root_block_device {
    volume_size = var.ebs_size
    volume_type = "gp3"
  }

  tags = {
    Name = "rhel8-instance"
  }
}

output "rhel_instance_id" {
  value = aws_instance.rhel.id
}

output "rhel_public_ip" {
  value = aws_instance.rhel.public_ip
}
