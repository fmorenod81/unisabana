# --- Public ALB in vpcn ---
resource "aws_lb" "public_alb" {
  name               = "public-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.pbsn1.id, aws_subnet.pbsn2.id]
  tags               = { Name = "public-alb" }
}

resource "aws_lb_target_group" "web_tg" {
  name     = "web-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.vpcn.id
}

resource "aws_lb_listener" "web_listener" {
  load_balancer_arn = aws_lb.public_alb.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_tg.arn
  }
}

# --- Web ASG ---
resource "aws_launch_template" "web_lt" {
  name_prefix   = "web-lt-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.keypair_name

  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = 8
    }
  }

  metadata_options {
    http_tokens = "optional"
  }

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.web_sg.id]
  }

  user_data = base64encode(<<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y docker
              # Using IMDSv1 for basic metadata access
              INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
              echo "Instance ID: $INSTANCE_ID" >> /var/log/user-data.log
              systemctl start docker
              systemctl enable docker
              docker run -d -p 80:80 -e APPSERVER=http://${aws_lb.internal_nlb.dns_name}:8080 benpiper/mtwa:web
              EOF
  )
}

resource "aws_autoscaling_group" "web_asg" {
  desired_capacity    = 1
  max_size            = 1
  min_size            = 1
  target_group_arns   = [aws_lb_target_group.web_tg.arn]
  vpc_zone_identifier = [aws_subnet.pbsn1.id, aws_subnet.pbsn2.id]

  depends_on = [
    aws_lb_listener.app_listener,
    aws_lb_target_group_attachment.app1,
    aws_lb_target_group_attachment.app2
  ]

  launch_template {
    id      = aws_launch_template.web_lt.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "web-asg-instance"
    propagate_at_launch = true
  }
}

# --- Scaling Policy ---
resource "aws_autoscaling_policy" "cpu_scaling" {
  name                   = "cpu-scaling-policy"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.web_asg.name
  policy_type            = "SimpleScaling"
}