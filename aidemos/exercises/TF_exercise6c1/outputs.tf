output "alb_dns_name" {
  description = "DNS name for the public ALB"
  value       = aws_lb.alb.dns_name
}

output "nlb_dns_name" {
  description = "DNS name for the internal NLB"
  value       = aws_lb.nlb.dns_name
}

output "web_instance_ips" {
  description = "Private IPs of web instances"
  value       = aws_instance.web[*].private_ip
}

output "app_instance_ips" {
  description = "Private IPs of app instances"
  value       = aws_instance.app[*].private_ip
}

output "web_vpc_id" {
  description = "Web VPC ID"
  value       = aws_vpc.web.id
}

output "app_vpc_id" {
  description = "App VPC ID"
  value       = aws_vpc.app.id
}

output "vpc_peering_connection_id" {
  description = "VPC peering connection ID"
  value       = aws_vpc_peering_connection.web_app.id
}
