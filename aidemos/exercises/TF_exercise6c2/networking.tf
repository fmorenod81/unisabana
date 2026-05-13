# --- VPC N (Web) ---
resource "aws_vpc" "vpcn" {
  cidr_block           = var.vpcn_cidr
  enable_dns_hostnames = true
  tags = { Name = "vpcn" }
}

resource "aws_internet_gateway" "vpcn_igw" {
  vpc_id = aws_vpc.vpcn.id
  tags   = { Name = "vpcn-igw" }
}

resource "aws_subnet" "pbsn1" {
  vpc_id            = aws_vpc.vpcn.id
  cidr_block        = cidrsubnet(var.vpcn_cidr, 8, 1)
  availability_zone = "${var.region}a"
  map_public_ip_on_launch = true
  tags = { Name = "pbsn1" }
}

resource "aws_subnet" "pbsn2" {
  vpc_id            = aws_vpc.vpcn.id
  cidr_block        = cidrsubnet(var.vpcn_cidr, 8, 2)
  availability_zone = "${var.region}b"
  map_public_ip_on_launch = true
  tags = { Name = "pbsn2" }
}

resource "aws_route_table" "vpcn_public" {
  vpc_id = aws_vpc.vpcn.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.vpcn_igw.id
  }
  route {
    cidr_block                = var.vpcp_cidr
    vpc_peering_connection_id = aws_vpc_peering_connection.peer.id
  }
  tags = { Name = "vpcn-public-rt" }
}

resource "aws_route_table_association" "pbsn1" {
  subnet_id      = aws_subnet.pbsn1.id
  route_table_id = aws_route_table.vpcn_public.id
}

resource "aws_route_table_association" "pbsn2" {
  subnet_id      = aws_subnet.pbsn2.id
  route_table_id = aws_route_table.vpcn_public.id
}

# --- VPC P (App) ---
resource "aws_vpc" "vpcp" {
  cidr_block           = var.vpcp_cidr
  enable_dns_hostnames = true
  tags = { Name = "vpcp" }
}

resource "aws_internet_gateway" "vpcp_igw" {
  vpc_id = aws_vpc.vpcp.id
  tags   = { Name = "vpcp-igw" }
}

resource "aws_subnet" "psn1" {
  vpc_id            = aws_vpc.vpcp.id
  cidr_block        = cidrsubnet(var.vpcp_cidr, 8, 1)
  availability_zone = "${var.region}a"
  tags = { Name = "psn1" }
}

resource "aws_subnet" "psn2" {
  vpc_id            = aws_vpc.vpcp.id
  cidr_block        = cidrsubnet(var.vpcp_cidr, 8, 2)
  availability_zone = "${var.region}b"
  tags = { Name = "psn2" }
}

resource "aws_subnet" "psn3" {
  vpc_id            = aws_vpc.vpcp.id
  cidr_block        = cidrsubnet(var.vpcp_cidr, 8, 3)
  availability_zone = "${var.region}c"
  map_public_ip_on_launch = true
  tags = { Name = "psn3" }
}

# NAT Gateway for vpcp private subnets
resource "aws_eip" "nat" {
  domain = "vpc"
}

resource "aws_nat_gateway" "vpcp_nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.psn3.id
  tags          = { Name = "vpcp-nat" }
}

resource "aws_route_table" "vpcp_private" {
  vpc_id = aws_vpc.vpcp.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.vpcp_nat.id
  }
  route {
    cidr_block                = var.vpcn_cidr
    vpc_peering_connection_id = aws_vpc_peering_connection.peer.id
  }
  tags = { Name = "vpcp-private-rt" }
}

resource "aws_route_table_association" "psn1" {
  subnet_id      = aws_subnet.psn1.id
  route_table_id = aws_route_table.vpcp_private.id
}

resource "aws_route_table_association" "psn2" {
  subnet_id      = aws_subnet.psn2.id
  route_table_id = aws_route_table.vpcp_private.id
}

resource "aws_route_table" "vpcp_public" {
  vpc_id = aws_vpc.vpcp.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.vpcp_igw.id
  }
  route {
    cidr_block                = var.vpcn_cidr
    vpc_peering_connection_id = aws_vpc_peering_connection.peer.id
  }
  tags = { Name = "vpcp-public-rt" }
}

resource "aws_route_table_association" "psn3" {
  subnet_id      = aws_subnet.psn3.id
  route_table_id = aws_route_table.vpcp_public.id
}

# --- VPC Peering ---
resource "aws_vpc_peering_connection" "peer" {
  vpc_id      = aws_vpc.vpcn.id
  peer_vpc_id = aws_vpc.vpcp.id
  auto_accept = true
  tags = { Name = "vpcn-vpcp-peering" }
}