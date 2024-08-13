resource "aws_main_route_table_association" "tfer--vpc-002D-08b42185f0b71ba2e" {
  route_table_id = "${data.terraform_remote_state.local.outputs.aws_route_table_tfer--rtb-002D-0f83435245b2e7e58_id}"
  vpc_id         = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}