resource "aws_route_table" "tfer--rtb-002D-01b25eb47f2fcc34c" {
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "igw-0604e89a1ce8a0102"
  }

  tags = {
    Name = "ariel-1-rtb-public"
  }

  tags_all = {
    Name = "ariel-1-rtb-public"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}

resource "aws_route_table" "tfer--rtb-002D-092a052855b3f6873" {
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = "nat-0840c661a8c6dc129"
  }

  tags = {
    Name = "ariel-1-rtb-private-2a"
  }

  tags_all = {
    Name = "ariel-1-rtb-private-2a"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}

resource "aws_route_table" "tfer--rtb-002D-0d8e5fdd2f6fff469" {
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = "nat-0b26edcdaed3af107"
  }

  tags = {
    Name = "ariel-1-rtb-private-2c"
  }

  tags_all = {
    Name = "ariel-1-rtb-private-2c"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}

resource "aws_route_table" "tfer--rtb-002D-0f83435245b2e7e58" {
  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}
