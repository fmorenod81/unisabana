variable "lab_key_name" {
  description = "Name of the existing EC2 KeyPair for SSH access to lab instances"
  type        = string
}

locals {
  lab_vpc_cidr     = "10.10.0.0/16"
  lab_public_cidr  = "10.10.1.0/24"
  lab_private_cidr = "10.10.2.0/24"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# --- VPC and subnets ---

resource "aws_vpc" "lab" {
  cidr_block           = local.lab_vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "vpcn"
  }
}

resource "aws_subnet" "lab_public" {
  vpc_id                  = aws_vpc.lab.id
  cidr_block              = local.lab_public_cidr
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "pbsn1"
  }
}

resource "aws_subnet" "lab_private" {
  vpc_id            = aws_vpc.lab.id
  cidr_block        = local.lab_private_cidr
  availability_zone = "us-east-1b"

  tags = {
    Name = "prsn2"
  }
}

# --- Internet Gateway ---

resource "aws_internet_gateway" "lab" {
  vpc_id = aws_vpc.lab.id

  tags = {
    Name = "lab-igw"
  }
}

# --- NAT Gateway in the public subnet ---

resource "aws_eip" "lab_nat" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.lab]

  tags = {
    Name = "lab-nat-eip"
  }
}

resource "aws_nat_gateway" "lab" {
  allocation_id = aws_eip.lab_nat.id
  subnet_id     = aws_subnet.lab_public.id
  depends_on    = [aws_internet_gateway.lab]

  tags = {
    Name = "lab-nat-gw"
  }
}

# --- Route tables ---

resource "aws_route_table" "lab_public" {
  vpc_id = aws_vpc.lab.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.lab.id
  }

  tags = {
    Name = "Route Table - Public"
  }
}

resource "aws_route_table" "lab_private" {
  vpc_id = aws_vpc.lab.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.lab.id
  }

  tags = {
    Name = "Route Table - Private"
  }
}

resource "aws_route_table_association" "lab_public" {
  subnet_id      = aws_subnet.lab_public.id
  route_table_id = aws_route_table.lab_public.id
}

resource "aws_route_table_association" "lab_private" {
  subnet_id      = aws_subnet.lab_private.id
  route_table_id = aws_route_table.lab_private.id
}

# --- Security group (shared by both instances per diagram) ---

resource "aws_security_group" "lab" {
  name        = "lab-sg"
  description = "Allow SSH, HTTP (Python web server) and all egress"
  vpc_id      = aws_vpc.lab.id

  ingress {
    description = "SSH from anywhere (public) and from within VPC (private)"
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
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lab-sg"
  }
}

# --- Instances ---

locals {
  python_web_server_user_data = <<-EOF
    #!/bin/bash
    set -eux
    dnf install -y python3
    mkdir -p /var/www/simple
    echo "<h1>Hello from $(hostname -f)</h1>" > /var/www/simple/index.html
    cat <<'UNIT' > /etc/systemd/system/pyhttp.service
    [Unit]
    Description=Simple Python HTTP server on port 8000
    After=network-online.target
    Wants=network-online.target

    [Service]
    Type=simple
    WorkingDirectory=/var/www/simple
    ExecStart=/usr/bin/python3 -m http.server 8000
    Restart=always

    [Install]
    WantedBy=multi-user.target
    UNIT
    systemctl daemon-reload
    systemctl enable --now pyhttp.service
  EOF
}

resource "aws_instance" "lab_public" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = "t3.micro"
  key_name                    = var.lab_key_name
  subnet_id                   = aws_subnet.lab_public.id
  vpc_security_group_ids      = [aws_security_group.lab.id]
  associate_public_ip_address = true
  user_data                   = local.python_web_server_user_data

  tags = {
    Name = "lab-public-instance"
  }
}

resource "aws_instance" "lab_private" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  key_name               = var.lab_key_name
  subnet_id              = aws_subnet.lab_private.id
  vpc_security_group_ids = [aws_security_group.lab.id]
  user_data              = local.python_web_server_user_data

  tags = {
    Name = "lab-private-instance"
  }
}

# --- Outputs ---

output "lab_public_instance_ip" {
  value = aws_instance.lab_public.public_ip
}

output "lab_private_instance_ip" {
  value = aws_instance.lab_private.private_ip
}

output "lab_nat_gateway_ip" {
  value = aws_eip.lab_nat.public_ip
}
