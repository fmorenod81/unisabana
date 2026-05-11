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

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_vpc" "vpcn" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "vpcn"
  }
}

resource "aws_subnet" "pbsn1" {
  vpc_id                  = aws_vpc.vpcn.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 1)
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "pbsn1"
  }
}

resource "aws_subnet" "prsn2" {
  vpc_id            = aws_vpc.vpcn.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 2)
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "prsn2"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpcn.id

  tags = {
    Name = "vpcn-igw"
  }
}

resource "aws_eip" "nat_eip" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]

  tags = {
    Name = "nat-eip"
  }
}

resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.pbsn1.id
  depends_on    = [aws_internet_gateway.igw]

  tags = {
    Name = "nat-gw"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.vpcn.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "rt-public"
  }
}

resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.vpcn.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }

  tags = {
    Name = "rt-private"
  }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.pbsn1.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "private_assoc" {
  subnet_id      = aws_subnet.prsn2.id
  route_table_id = aws_route_table.private_rt.id
}

resource "aws_security_group" "instance_sg" {
  name        = "vpcn-instance-sg"
  description = "Allow SSH and Python web server"
  vpc_id      = aws_vpc.vpcn.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Python simple HTTP server"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "ICMP from VPC"
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "vpcn-instance-sg"
  }
}

resource "aws_instance" "public_web" {
  ami                         = data.aws_ami.amazon_linux_2.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.pbsn1.id
  vpc_security_group_ids      = [aws_security_group.instance_sg.id]
  key_name                    = var.key_pair_name
  associate_public_ip_address = true

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y python3
              mkdir -p /home/ec2-user/www
              echo "<h1>Hello from pbsn1 public web server</h1>" > /home/ec2-user/www/index.html
              cd /home/ec2-user/www && nohup python3 -m http.server 8000 > /var/log/pyserver.log 2>&1 &
              EOF

  tags = {
    Name = "public-web-server"
  }
}

resource "aws_instance" "private_app" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.prsn2.id
  vpc_security_group_ids = [aws_security_group.instance_sg.id]
  key_name               = var.key_pair_name

  tags = {
    Name = "private-app-server"
  }
}
