# AWS Infrastructure with Terraform (TF_ex5)

This Terraform configuration creates a complete AWS infrastructure with EC2 instance, VPC, security groups, and network interfaces as shown in the architectural diagram.

## Architecture Overview

- **VPC**: Custom VPC with CIDR block (default: 10.0.0.0/16)
- **Subnet**: Public subnet for EC2 instance
- **Internet Gateway**: For public internet access
- **Security Group**: Allows HTTP (80), HTTPS (443), and SSH (22)
- **EC2 Instance**: On-demand T3 instance with Docker support
- **ENI**: Elastic Network Interface attached to the EC2 instance
- **EIP**: Elastic IP for static public IP address
- **User Data**: Automatically installs Docker and runs hello-world and MTWA web service

## Prerequisites

1. AWS Account with appropriate credentials
2. Terraform installed (v1.0 or higher)
3. An existing EC2 Key Pair in your AWS account
4. AWS CLI configured with credentials (optional but recommended)

## Usage

### Step 1: Create terraform.tfvars

Copy the example file and update with your values:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set:
- `keypair_name`: Your EC2 Key Pair name (required)
- `vpc_cidr`: Your VPC CIDR block (optional, default: 10.0.0.0/16)
- `subnet_cidr`: Your subnet CIDR block (optional, default: 10.0.1.0/24)
- `aws_region`: AWS region (optional, default: us-east-1)

### Step 2: Initialize Terraform

```bash
terraform init
```

### Step 3: Review the Plan

```bash
terraform plan
```

### Step 4: Apply the Configuration

```bash
terraform apply
```

Confirm by typing `yes` when prompted.

### Step 5: Get Outputs

After deployment, Terraform will output:
- VPC ID
- Subnet ID
- Internet Gateway ID
- Security Group ID
- Network Interface ID
- Elastic IP Address
- EC2 Instance ID
- SSH connection command
- HTTP and HTTPS endpoints

## Access Your Instance

### Via SSH

```bash
ssh -i /path/to/your-keypair.pem ec2-user@<ELASTIC_IP>
```

### Docker Services

- **Hello-World**: http://<ELASTIC_IP>
- **MTWA Web Service**: https://<ELASTIC_IP>

## Customization

### Change Instance Type

Edit `terraform.tfvars`:
```
instance_type = "t3.small"  # or any other t3 size
```

### Change CIDR Blocks

Edit `terraform.tfvars`:
```
vpc_cidr    = "172.16.0.0/16"
subnet_cidr = "172.16.1.0/24"
```

### Add More Security Group Rules

Edit `security.tf` and add more `aws_vpc_security_group_ingress_rule` resources.

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

Confirm by typing `yes` when prompted.

## Files Description

- **main.tf**: Provider configuration
- **variables.tf**: Input variables definition
- **vpc.tf**: VPC, Subnet, Internet Gateway, and Route Table
- **security.tf**: Security Group with inbound/outbound rules
- **network.tf**: EC2 instance, ENI, EIP, and IAM resources
- **outputs.tf**: Output values
- **terraform.tfvars.example**: Example variables file

## Notes

- The EC2 instance uses an on-demand instance (not spot)
- User data script runs automatically when the instance launches
- The EIP is associated with the ENI, ensuring consistent public IP
- All resources are tagged for easy management and cost tracking
- The security group allows all outbound traffic by default

## Troubleshooting

### Key Pair Not Found Error

Ensure the key pair exists in your AWS account in the specified region:
```bash
aws ec2 describe-key-pairs --region us-east-1
```

### Cannot Connect via SSH

1. Verify security group allows SSH (port 22)
2. Verify the key pair is correct
3. Check that the instance is running: `aws ec2 describe-instances`
4. Ensure your IP is not blocked by a restrictive security group rule

### Docker Services Not Running

Check instance logs:
```bash
aws ec2 get-console-output --instance-id <INSTANCE_ID> --region us-east-1
```
