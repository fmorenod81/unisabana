variable "peer_key_name" {
  description = "Name of the existing EC2 KeyPair for SSH access to peering lab instances"
  type        = string
}

variable "peer_bucket_name" {
  description = "Name of the EXISTING private S3 bucket reached via the VPC endpoint"
  type        = string
}

locals {
  vpcn_cidr        = "10.20.0.0/16"
  vpcn_public_cidr = "10.20.1.0/24"
  vpcp_cidr        = "10.30.0.0/16"
  vpcp_private_cidr = "10.30.1.0/24"
}

data "aws_region" "current" {}

data "aws_ami" "peer_amazon_linux" {
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

# =====================================================================
# VPC "vpcn" -- public side with IGW
# =====================================================================

resource "aws_vpc" "vpcn" {
  cidr_block           = local.vpcn_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "vpcn"
  }
}

resource "aws_subnet" "vpcn_public" {
  vpc_id                  = aws_vpc.vpcn.id
  cidr_block              = local.vpcn_public_cidr
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "pbsn1"
  }
}

resource "aws_internet_gateway" "vpcn" {
  vpc_id = aws_vpc.vpcn.id

  tags = {
    Name = "vpcn-igw"
  }
}

resource "aws_route_table" "vpcn_public" {
  vpc_id = aws_vpc.vpcn.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.vpcn.id
  }

  route {
    cidr_block                = local.vpcp_cidr
    vpc_peering_connection_id = aws_vpc_peering_connection.vpcn_to_vpcp.id
  }

  tags = {
    Name = "vpcn-public-rt"
  }
}

resource "aws_route_table_association" "vpcn_public" {
  subnet_id      = aws_subnet.vpcn_public.id
  route_table_id = aws_route_table.vpcn_public.id
}

# =====================================================================
# VPC "vpcp" -- private side, no Internet, S3 via gateway endpoint
# =====================================================================

resource "aws_vpc" "vpcp" {
  cidr_block           = local.vpcp_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "vpcp"
  }
}

resource "aws_subnet" "vpcp_private" {
  vpc_id            = aws_vpc.vpcp.id
  cidr_block        = local.vpcp_private_cidr
  availability_zone = "us-east-1a"

  tags = {
    Name = "prsn2"
  }
}

resource "aws_route_table" "vpcp_private" {
  vpc_id = aws_vpc.vpcp.id

  route {
    cidr_block                = local.vpcn_cidr
    vpc_peering_connection_id = aws_vpc_peering_connection.vpcn_to_vpcp.id
  }

  tags = {
    Name = "vpcp-private-rt"
  }
}

resource "aws_route_table_association" "vpcp_private" {
  subnet_id      = aws_subnet.vpcp_private.id
  route_table_id = aws_route_table.vpcp_private.id
}

# --- VPC Peering ---

resource "aws_vpc_peering_connection" "vpcn_to_vpcp" {
  vpc_id      = aws_vpc.vpcn.id
  peer_vpc_id = aws_vpc.vpcp.id
  auto_accept = true

  tags = {
    Name = "vpcn-vpcp-peering"
  }
}

# --- S3 Gateway VPC Endpoint in vpcp (route attached to private RT) ---

resource "aws_vpc_endpoint" "vpcp_s3" {
  vpc_id            = aws_vpc.vpcp.id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.vpcp_private.id]

  tags = {
    Name = "vpcp-s3-endpoint"
  }
}

# =====================================================================
# Security Groups
# =====================================================================

resource "aws_security_group" "vpcn_public" {
  name        = "vpcn-public-sg"
  description = "Allow SSH and HTTP (Python on port 80) from anywhere"
  vpc_id      = aws_vpc.vpcn.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP (Python web server)"
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
    Name = "vpcn-public-sg"
  }
}

resource "aws_security_group" "vpcp_private" {
  name        = "vpcp-private-sg"
  description = "Allow SSH only from vpcn over peering; egress to S3 prefix list"
  vpc_id      = aws_vpc.vpcp.id

  ingress {
    description = "SSH from vpcn via peering"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [local.vpcn_cidr]
  }

  egress {
    description     = "HTTPS to S3 via gateway endpoint"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    prefix_list_ids = [aws_vpc_endpoint.vpcp_s3.prefix_list_id]
  }

  egress {
    description = "Return traffic to vpcn over peering"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [local.vpcn_cidr]
  }

  tags = {
    Name = "vpcp-private-sg"
  }
}

# =====================================================================
# Instances
# =====================================================================

locals {
  python_port80_user_data = <<-EOF
    #!/bin/bash
    set -eux
    dnf install -y python3
    mkdir -p /var/www/simple
    echo "<h1>Hello from $(hostname -f)</h1>" > /var/www/simple/index.html
    cat <<'UNIT' > /etc/systemd/system/pyhttp.service
    [Unit]
    Description=Simple Python HTTP server on port 80
    After=network-online.target
    Wants=network-online.target

    [Service]
    Type=simple
    WorkingDirectory=/var/www/simple
    ExecStart=/usr/bin/python3 -m http.server 80
    Restart=always

    [Install]
    WantedBy=multi-user.target
    UNIT
    systemctl daemon-reload
    systemctl enable --now pyhttp.service
  EOF
}

resource "aws_instance" "vpcn_public" {
  ami                         = data.aws_ami.peer_amazon_linux.id
  instance_type               = "t3.micro"
  key_name                    = var.peer_key_name
  subnet_id                   = aws_subnet.vpcn_public.id
  vpc_security_group_ids      = [aws_security_group.vpcn_public.id]
  associate_public_ip_address = true
  user_data                   = local.python_port80_user_data

  tags = {
    Name = "vpcn-public-instance"
  }
}

resource "aws_instance" "vpcp_private" {
  ami                    = data.aws_ami.peer_amazon_linux.id
  instance_type          = "t3.micro"
  key_name               = var.peer_key_name
  subnet_id              = aws_subnet.vpcp_private.id
  vpc_security_group_ids = [aws_security_group.vpcp_private.id]

  tags = {
    Name = "vpcp-private-instance"
  }
}

# =====================================================================
# Outputs
# =====================================================================

output "vpcn_public_instance_ip" {
  value = aws_instance.vpcn_public.public_ip
}

output "vpcp_private_instance_ip" {
  value = aws_instance.vpcp_private.private_ip
}

output "private_bucket_name" {
  value = var.peer_bucket_name
}
