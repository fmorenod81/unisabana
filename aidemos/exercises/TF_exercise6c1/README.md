# TF_exercise6c1

Terraform exercise for a two-VPC Docker architecture using AWS.

## Architecture

- Top VPC (`vpc-web`) with two public subnets: `pbsn1`, `pbsn2`
- Public Application Load Balancer in the top VPC
- Two EC2 web instances running `fmorenod81/mtwa:web` on port 80
- Bottom VPC (`vpc-app`) with two private subnets: `psn1`, `psn2`
- Private app EC2 instances running `fmorenod81/mtwa:app` on port 8080
- Internal Network Load Balancer in the bottom VPC
- VPC peering between the two VPCs
- NAT gateway in the bottom VPC public subnet `psn3`

## Usage

1. Create or import an EC2 key pair in the target region.
2. Run:

```bash
terraform init
terraform plan -var="keypair_name=<your-key-name>"
terraform apply -var="keypair_name=<your-key-name>"
```

3. Use the `alb_dns_name` output to reach the public web service.

## Notes

- `fmorenod81/mtwa:web` is deployed with `ENV` set to the internal NLB DNS name from `aws_lb.nlb`.
- Default ALB and NLB health checks are used.
