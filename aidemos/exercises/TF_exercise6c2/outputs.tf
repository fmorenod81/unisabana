output "alb_dns_name" {
  value = aws_lb.public_alb.dns_name
}

output "internal_nlb_dns_name" {
  value = aws_lb.internal_nlb.dns_name
}