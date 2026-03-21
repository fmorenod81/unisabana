resource "aws_lb" "main" {
  name               = "ALB"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = {
    Name = "ALB on Port 80"
  }
}

resource "aws_lb_target_group" "port80" {
  name     = "TG-Port80"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
  }
}

resource "aws_lb_target_group" "port81" {
  name     = "TG-Port81"
  port     = 81
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    port                = "81"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
  }
}

resource "aws_lb_target_group" "port82" {
  name     = "TG-Port82"
  port     = 82
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    port                = "82"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
  }
}



resource "aws_lb_target_group_attachment" "port80_web" {
  target_group_arn = aws_lb_target_group.port80.arn
  target_id        = aws_instance.web.id
  port             = 80
}

resource "aws_lb_target_group_attachment" "port80_benpiper" {
  target_group_arn = aws_lb_target_group.port80.arn
  target_id        = aws_instance.benpiper.id
  port             = 80
}

resource "aws_lb_target_group_attachment" "port81_web" {
  target_group_arn = aws_lb_target_group.port81.arn
  target_id        = aws_instance.web.id
  port             = 81
}

resource "aws_lb_target_group_attachment" "port81_benpiper" {
  target_group_arn = aws_lb_target_group.port81.arn
  target_id        = aws_instance.benpiper.id
  port             = 81
}

resource "aws_lb_target_group_attachment" "port82_web" {
  target_group_arn = aws_lb_target_group.port82.arn
  target_id        = aws_instance.web.id
  port             = 82
}

resource "aws_lb_target_group_attachment" "port82_benpiper" {
  target_group_arn = aws_lb_target_group.port82.arn
  target_id        = aws_instance.benpiper.id
  port             = 82
}



resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.port80.arn
  }
}

resource "aws_lb_listener" "port81" {
  load_balancer_arn = aws_lb.main.arn
  port              = 81
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.port81.arn
  }
}

resource "aws_lb_listener" "port82" {
  load_balancer_arn = aws_lb.main.arn
  port              = 82
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.port82.arn
  }
}

resource "aws_lb_listener_rule" "port81" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.port81.arn
  }

  condition {
    path_pattern {
      values = ["/port81"]
    }
  }
}

resource "aws_lb_listener_rule" "port82" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 101

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.port82.arn
  }

  condition {
    path_pattern {
      values = ["/port82"]
    }
  }
}


