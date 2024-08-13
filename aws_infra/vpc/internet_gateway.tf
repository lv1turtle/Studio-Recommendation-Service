resource "aws_internet_gateway" "tfer--igw-002D-0604e89a1ce8a0102" {
  tags = {
    Name = "ariel-1-airflow-igw"
  }

  tags_all = {
    Name = "ariel-1-airflow-igw"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}