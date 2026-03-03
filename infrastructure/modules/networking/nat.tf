// Elastic IPs for NAT Gateways
resource "aws_eip" "nat_1" {
  domain = "vpc"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}nat-eip-1"
    }
  )
}

resource "aws_eip" "nat_2" {
  domain = "vpc"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}nat-eip-2"
    }
  )
}

// NAT Gateways in public subnets
resource "aws_nat_gateway" "nat_1" {
  allocation_id = aws_eip.nat_1.id
  subnet_id     = aws_subnet.public_1.id
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}nat-gateway-1"
    }
  )
  
  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "nat_2" {
  allocation_id = aws_eip.nat_2.id
  subnet_id     = aws_subnet.public_2.id
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}nat-gateway-2"
    }
  )
  
  depends_on = [aws_internet_gateway.main]
}
