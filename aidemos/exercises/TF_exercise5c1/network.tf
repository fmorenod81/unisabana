# User data script for Docker
locals {
  user_data = base64encode(<<-EOF
              #!/bin/bash
              set -e
              
              # Update system packages
              apt-get update
              apt-get install -y docker.io
              
              # Start Docker service
              systemctl start docker
              systemctl enable docker
              
              # Run Docker hello-world
              docker run hello-world
              
              # Run MTWA web service
              docker run -d -p 80:80 benpiper/mtwa:web
              EOF
  )
}

# Network Interface (ENI)
resource "aws_network_interface" "main" {
  subnet_id           = aws_subnet.public.id
  security_groups     = [aws_security_group.main.id]
  
  tags = {
    Name        = "eni-main"
    Environment = var.environment_tag
  }
}

# Elastic IP
resource "aws_eip" "main" {
  domain               = "vpc"
  network_interface    = aws_network_interface.main.id
  depends_on           = [aws_internet_gateway.main]

  tags = {
    Name        = "eip-main"
    Environment = var.environment_tag
  }
}

# On-Demand EC2 Instance (T3)
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

  depends_on = [aws_internet_gateway.main]
}

# Get latest Amazon Linux 2 AMI
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
