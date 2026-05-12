output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "subnet_id" {
  description = "Public Subnet ID"
  value       = aws_subnet.public.id
}

output "internet_gateway_id" {
  description = "Internet Gateway ID"
  value       = aws_internet_gateway.main.id
}

output "security_group_id" {
  description = "Security Group ID"
  value       = aws_security_group.main.id
}

output "network_interface_id" {
  description = "Network Interface (ENI) ID"
  value       = aws_network_interface.main.id
}

output "elastic_ip" {
  description = "Elastic IP Address"
  value       = aws_eip.main.public_ip
}

output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.main.id
}

output "instance_private_ip" {
  description = "EC2 Instance Private IP"
  value       = aws_instance.main.private_ip
}

output "instance_public_ip" {
  description = "EC2 Instance Public IP (via EIP)"
  value       = aws_eip.main.public_ip
}

output "ssh_connection_string" {
  description = "SSH connection command"
  value       = "ssh -i /path/to/keypair.pem ec2-user@${aws_eip.main.public_ip}"
}

output "http_endpoint" {
  description = "HTTP endpoint for Docker container"
  value       = "http://${aws_eip.main.public_ip}"
}

output "https_endpoint" {
  description = "HTTPS endpoint for MTWA web service"
  value       = "https://${aws_eip.main.public_ip}"
}
