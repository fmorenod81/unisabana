output "public_instance_ip" {
  value       = aws_instance.public.public_ip
  description = "Public instance IP"
}

output "private_instance_ip" {
  value       = aws_instance.private.private_ip
  description = "Private instance IP"
}

output "nat_gateway_ip" {
  value       = aws_eip.nat.public_ip
  description = "NAT Gateway public IP"
}

output "vpc_id" {
  value = aws_vpc.main.id
}
