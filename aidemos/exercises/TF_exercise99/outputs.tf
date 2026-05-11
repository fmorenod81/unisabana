output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.vpcn.id
}

output "public_subnet_id" {
  description = "Public subnet ID (pbsn1)"
  value       = aws_subnet.pbsn1.id
}

output "private_subnet_id" {
  description = "Private subnet ID (prsn2)"
  value       = aws_subnet.prsn2.id
}

output "public_instance_public_ip" {
  description = "Public IP of the public web server"
  value       = aws_instance.public_web.public_ip
}

output "public_instance_private_ip" {
  description = "Private IP of the public web server"
  value       = aws_instance.public_web.private_ip
}

output "private_instance_private_ip" {
  description = "Private IP of the private app server"
  value       = aws_instance.private_app.private_ip
}

output "nat_gateway_public_ip" {
  description = "Public IP of the NAT Gateway"
  value       = aws_eip.nat_eip.public_ip
}

output "web_server_url" {
  description = "URL of the public web server"
  value       = "http://${aws_instance.public_web.public_ip}:8000"
}
