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

data "aws_availability_zones" "available" {
  state = "available"
}

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

locals {
  web_userdata = base64encode(<<-EOF
    #!/bin/bash
    set -e

    yum update -y
    yum install -y docker
    systemctl enable --now docker

    docker run -d -p 80:80 -e APPSERVER="http://${aws_lb.nlb.dns_name}:8080" fmorenod81/mtwa:web
    EOF
  )

  app_userdata = base64encode(<<-EOF
    #!/bin/bash
    set -e

    yum update -y
    yum install -y docker
    systemctl enable --now docker

    docker run -d -p 8080:8080 fmorenod81/mtwa:app
    EOF
  )
}

resource "aws_vpc" "web" {
  cidr_block           = var.web_vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "vpc-web"
    Environment = var.environment_tag
  }
}

resource "aws_vpc" "app" {
  cidr_block           = var.app_vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "vpc-app"
    Environment = var.environment_tag
  }
}

resource "aws_subnet" "pbsn1" {
  vpc_id                  = aws_vpc.web.id
  cidr_block              = var.web_public_subnet1_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name        = "pbsn1"
    Environment = var.environment_tag
  }
}

resource "aws_subnet" "pbsn2" {
  vpc_id                  = aws_vpc.web.id
  cidr_block              = var.web_public_subnet2_cidr
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name        = "pbsn2"
    Environment = var.environment_tag
  }
}

resource "aws_subnet" "psn1" {
  vpc_id            = aws_vpc.app.id
  cidr_block        = var.app_private_subnet1_cidr
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name        = "psn1"
    Environment = var.environment_tag
  }
}

resource "aws_subnet" "psn2" {
  vpc_id            = aws_vpc.app.id
  cidr_block        = var.app_private_subnet2_cidr
  availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name        = "psn2"
    Environment = var.environment_tag
  }
}

resource "aws_subnet" "psn3" {
  vpc_id                  = aws_vpc.app.id
  cidr_block              = var.app_public_subnet_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name        = "psn3"
    Environment = var.environment_tag
  }
}

resource "aws_internet_gateway" "web" {
  vpc_id = aws_vpc.web.id

  tags = {
    Name        = "igw-web"
    Environment = var.environment_tag
  }
}

resource "aws_internet_gateway" "app" {
  vpc_id = aws_vpc.app.id

  tags = {
    Name        = "igw-app"
    Environment = var.environment_tag
  }
}

resource "aws_route_table" "web_public" {
  vpc_id = aws_vpc.web.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.web.id
  }

  tags = {
    Name        = "rt-web-public"
    Environment = var.environment_tag
  }
}

resource "aws_route_table_association" "web_public_pbsn1" {
  subnet_id      = aws_subnet.pbsn1.id
  route_table_id = aws_route_table.web_public.id
}

resource "aws_route_table_association" "web_public_pbsn2" {
  subnet_id      = aws_subnet.pbsn2.id
  route_table_id = aws_route_table.web_public.id
}

resource "aws_route_table" "app_public" {
  vpc_id = aws_vpc.app.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.app.id
  }

  tags = {
    Name        = "rt-app-public"
    Environment = var.environment_tag
  }
}

resource "aws_route_table_association" "app_public_psn3" {
  subnet_id      = aws_subnet.psn3.id
  route_table_id = aws_route_table.app_public.id
}

resource "aws_eip" "nat" {
  vpc = true

  tags = {
    Name        = "eip-nat"
    Environment = var.environment_tag
  }
}

resource "aws_nat_gateway" "app" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.psn3.id

  tags = {
    Name        = "nat-app"
    Environment = var.environment_tag
  }
}

resource "aws_route_table" "app_private" {
  vpc_id = aws_vpc.app.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.app.id
  }

  tags = {
    Name        = "rt-app-private"
    Environment = var.environment_tag
  }
}

resource "aws_route_table_association" "app_private_psn1" {
  subnet_id      = aws_subnet.psn1.id
  route_table_id = aws_route_table.app_private.id
}

resource "aws_route_table_association" "app_private_psn2" {
  subnet_id      = aws_subnet.psn2.id
  route_table_id = aws_route_table.app_private.id
}

resource "aws_vpc_peering_connection" "web_app" {
  vpc_id        = aws_vpc.web.id
  peer_vpc_id   = aws_vpc.app.id
  auto_accept   = true

  tags = {
    Name        = "peering-web-app"
    Environment = var.environment_tag
  }
}

resource "aws_route" "web_to_app" {
  route_table_id         = aws_route_table.web_public.id
  destination_cidr_block = aws_vpc.app.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.web_app.id
}

resource "aws_route" "web_to_psn1" {
  route_table_id         = aws_route_table.web_public.id
  destination_cidr_block = var.app_private_subnet1_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.web_app.id
}

resource "aws_route" "web_to_psn2" {
  route_table_id         = aws_route_table.web_public.id
  destination_cidr_block = var.app_private_subnet2_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.web_app.id
}

resource "aws_route" "web_to_psn3" {
  route_table_id         = aws_route_table.web_public.id
  destination_cidr_block = var.app_public_subnet_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.web_app.id
}

resource "aws_route" "app_to_web" {
  route_table_id         = aws_route_table.app_public.id
  destination_cidr_block = aws_vpc.web.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.web_app.id
}

resource "aws_route" "app_public_to_pbsn1" {
  route_table_id         = aws_route_table.app_public.id
  destination_cidr_block = var.web_public_subnet1_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.web_app.id
}

resource "aws_route" "app_public_to_pbsn2" {
  route_table_id         = aws_route_table.app_public.id
  destination_cidr_block = var.web_public_subnet2_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.web_app.id
}

resource "aws_route" "app_private_to_web" {
  route_table_id         = aws_route_table.app_private.id
  destination_cidr_block = aws_vpc.web.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.web_app.id
}

resource "aws_route" "app_private_to_pbsn1" {
  route_table_id         = aws_route_table.app_private.id
  destination_cidr_block = var.web_public_subnet1_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.web_app.id
}

resource "aws_route" "app_private_to_pbsn2" {
  route_table_id         = aws_route_table.app_private.id
  destination_cidr_block = var.web_public_subnet2_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.web_app.id
}

resource "aws_security_group" "alb" {
  name_prefix = "alb-"
  description = "Allow HTTP from internet to ALB"
  vpc_id      = aws_vpc.web.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "sg-alb"
    Environment = var.environment_tag
  }
}

resource "aws_security_group" "web_instances" {
  name_prefix = "web-"
  description = "Allow traffic from ALB and SSH for web instances"
  vpc_id      = aws_vpc.web.id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "sg-web"
    Environment = var.environment_tag
  }
}

resource "aws_security_group" "app_instances" {
  name_prefix = "app-"
  description = "Allow traffic to app instances from NLB and web VPC"
  vpc_id      = aws_vpc.app.id

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.web.cidr_block, aws_vpc.app.cidr_block]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "sg-app"
    Environment = var.environment_tag
  }
}

resource "aws_lb" "alb" {
  name               = "alb-web"
  internal           = false
  load_balancer_type = "application"
  subnets            = [aws_subnet.pbsn1.id, aws_subnet.pbsn2.id]
  security_groups    = [aws_security_group.alb.id]

  tags = {
    Name        = "alb-web"
    Environment = var.environment_tag
  }
}

resource "aws_lb_target_group" "web" {
  name        = "tg-web"
  port        = 80
  protocol    = "HTTP"
  target_type = "instance"
  vpc_id      = aws_vpc.web.id

  health_check {
    protocol = "HTTP"
    path     = "/"
  }

  tags = {
    Name        = "tg-web"
    Environment = var.environment_tag
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

resource "aws_lb" "nlb" {
  name               = "nlb-app"
  internal           = true
  load_balancer_type = "network"
  subnets            = [aws_subnet.psn1.id, aws_subnet.psn2.id]

  tags = {
    Name        = "nlb-app"
    Environment = var.environment_tag
  }
}

resource "aws_lb_target_group" "app" {
  name        = "tg-app"
  port        = 8080
  protocol    = "TCP"
  target_type = "instance"
  vpc_id      = aws_vpc.app.id

  health_check {
    protocol = "TCP"
  }

  tags = {
    Name        = "tg-app"
    Environment = var.environment_tag
  }
}

resource "aws_lb_listener" "nlb_listener" {
  load_balancer_arn = aws_lb.nlb.arn
  port              = 8080
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_instance" "web" {
  count         = 2
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.keypair_name
  subnet_id     = element([aws_subnet.pbsn1.id, aws_subnet.pbsn2.id], count.index)
  vpc_security_group_ids = [aws_security_group.web_instances.id]
  user_data     = local.web_userdata

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
  }

  tags = {
    Name        = "web-${count.index + 1}"
    Environment = var.environment_tag
  }
}

resource "aws_lb_target_group_attachment" "web" {
  count            = 2
  target_group_arn = aws_lb_target_group.web.arn
  target_id        = aws_instance.web[count.index].id
  port             = 80
}

resource "aws_instance" "app" {
  count         = 2
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.keypair_name
  subnet_id     = element([aws_subnet.psn1.id, aws_subnet.psn2.id], count.index)
  vpc_security_group_ids = [aws_security_group.app_instances.id]
  user_data     = local.app_userdata

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
  }

  tags = {
    Name        = "app-${count.index + 1}"
    Environment = var.environment_tag
  }
}

resource "aws_lb_target_group_attachment" "app" {
  count            = 2
  target_group_arn = aws_lb_target_group.app.arn
  target_id        = aws_instance.app[count.index].id
  port             = 8080
}
