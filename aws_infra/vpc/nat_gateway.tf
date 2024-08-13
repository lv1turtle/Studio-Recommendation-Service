resource "aws_nat_gateway" "tfer--nat-002D-0840c661a8c6dc129" {
  allocation_id                      = "eipalloc-0dbce4eb86a489d96"
  connectivity_type                  = "public"
  private_ip                         = "10.10.5.104"
  secondary_private_ip_address_count = "0"
  subnet_id                          = "subnet-04725e6917247af69"

  tags = {
    Name = "ariel-1-nat_2a"
  }

  tags_all = {
    Name = "ariel-1-nat_2a"
  }
}

resource "aws_nat_gateway" "tfer--nat-002D-0b26edcdaed3af107" {
  allocation_id                      = "eipalloc-0e246bd75199e0083"
  connectivity_type                  = "public"
  private_ip                         = "10.10.28.135"
  secondary_private_ip_address_count = "0"
  subnet_id                          = "subnet-056e44f08860420d9"

  tags = {
    Name = "ariel-1-nat_2c"
  }

  tags_all = {
    Name = "ariel-1-nat_2c"
  }
}