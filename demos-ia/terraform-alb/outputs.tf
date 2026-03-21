output "alb_dns_name" {
  value       = aws_lb.main.dns_name
  description = "ALB DNS name"
}

output "instance_web_ip" {
  value = aws_instance.web.public_ip
}

output "instance_benpiper_ip" {
  value = aws_instance.benpiper.public_ip
}


