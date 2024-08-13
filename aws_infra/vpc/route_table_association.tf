resource "aws_route_table_association" "tfer--subnet-002D-0dde2d2e14ae7f173" {
  route_table_id = "${data.terraform_remote_state.local.outputs.aws_route_table_tfer--rtb-002D-01b25eb47f2fcc34c_id}"
  subnet_id      = "${data.terraform_remote_state.local.outputs.aws_subnet_tfer--subnet-002D-0dde2d2e14ae7f173_id}"
}

resource "aws_route_table_association" "tfer--subnet-002D-01cc6b2f78678040e" {
  route_table_id = "${data.terraform_remote_state.local.outputs.aws_route_table_tfer--rtb-002D-092a052855b3f6873_id}"
  subnet_id      = "${data.terraform_remote_state.local.outputs.aws_subnet_tfer--subnet-002D-01cc6b2f78678040e_id}"
}

resource "aws_route_table_association" "tfer--subnet-002D-02580112e983f75fb" {
  route_table_id = "${data.terraform_remote_state.local.outputs.aws_route_table_tfer--rtb-002D-0d8e5fdd2f6fff469_id}"
  subnet_id      = "${data.terraform_remote_state.local.outputs.aws_subnet_tfer--subnet-002D-02580112e983f75fb_id}"
}