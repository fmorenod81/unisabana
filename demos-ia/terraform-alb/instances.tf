data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.instances.id]
  key_name               = var.key_name
  user_data              = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    service docker start
    docker run -d -p 80:80 ${var.docker_images.web}
    docker run -d -p 81:80 ${var.docker_images.benpiper}
    docker run -d -p 82:80 ${var.docker_images.hello}
  EOF

  tags = {
    Name = "us-east-1a"
  }
}

resource "aws_instance" "benpiper" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public[1].id
  vpc_security_group_ids = [aws_security_group.instances.id]
  key_name               = var.key_name
  user_data              = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    service docker start
    docker run -d -p 80:80 ${var.docker_images.web}
    docker run -d -p 81:80 ${var.docker_images.benpiper}
    docker run -d -p 82:80 ${var.docker_images.hello}
  EOF

  tags = {
    Name = "us-east-1"
  }
}
