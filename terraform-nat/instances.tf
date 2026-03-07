data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "public" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.instances.id]
  key_name               = var.key_name
  user_data              = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y python3
    python3 -m http.server 80
  EOF

  tags = {
    Name = "T2"
  }
}

resource "aws_instance" "private" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.private.id
  vpc_security_group_ids = [aws_security_group.instances.id]
  key_name               = var.key_name
  user_data              = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y python3
    python3 -m http.server 80
  EOF

  tags = {
    Name = "T2"
  }
}
