# --- Internal NLB in vpcp ---
resource "aws_lb" "internal_nlb" {
  name               = "app-nlb"
  internal           = true
  load_balancer_type = "network"
  subnets            = [aws_subnet.psn1.id, aws_subnet.psn2.id]
  security_groups    = [aws_security_group.nlb_sg.id]
  tags               = { Name = "internal-nlb" }
}

resource "aws_lb_target_group" "app_tg" {
  name     = "app-tg"
  port     = 8080
  protocol = "TCP"
  vpc_id   = aws_vpc.vpcp.id
}

resource "aws_lb_listener" "app_listener" {
  load_balancer_arn = aws_lb.internal_nlb.arn
  port              = 8080
  protocol          = "TCP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

# --- App Instances ---
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "app_server_1" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name               = var.keypair_name
  subnet_id              = aws_subnet.psn1.id
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  root_block_device {
    volume_size = 8
  }

  metadata_options {
    http_tokens = "optional"
  }

  user_data = <<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y docker
              # Using IMDSv1 for basic metadata access
              INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
              echo "Instance ID: $INSTANCE_ID" >> /var/log/user-data.log
              systemctl start docker
              systemctl enable docker
              docker run -d -p 8080:8080 benpiper/mtwa:app
              EOF

  tags = { Name = "app-server-1" }
}

resource "aws_instance" "app_server_2" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name               = var.keypair_name
  subnet_id              = aws_subnet.psn2.id
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  root_block_device {
    volume_size = 8
  }

  metadata_options {
    http_tokens = "optional"
  }

  user_data = <<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y docker
              # Using IMDSv1 for basic metadata access
              INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
              echo "Instance ID: $INSTANCE_ID" >> /var/log/user-data.log
              systemctl start docker
              systemctl enable docker
              docker run -d -p 8080:8080 benpiper/mtwa:app
              EOF

  tags = { Name = "app-server-2" }
}

resource "aws_lb_target_group_attachment" "app1" {
  target_group_arn = aws_lb_target_group.app_tg.arn
  target_id        = aws_instance.app_server_1.id
}

resource "aws_lb_target_group_attachment" "app2" {
  target_group_arn = aws_lb_target_group.app_tg.arn
  target_id        = aws_instance.app_server_2.id
}