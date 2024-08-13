resource "aws_subnet" "tfer--subnet-002D-04725e6917247af69" {
  assign_ipv6_address_on_creation                = "false"
  cidr_block                                     = "10.10.0.0/20"
  enable_dns64                                   = "false"
  enable_lni_at_device_index                     = "0"
  enable_resource_name_dns_a_record_on_launch    = "false"
  enable_resource_name_dns_aaaa_record_on_launch = "false"
  ipv6_native                                    = "false"
  map_customer_owned_ip_on_launch                = "false"
  map_public_ip_on_launch                        = "true"
  private_dns_hostname_type_on_launch            = "ip-name"

  tags = {
    Name = "ariel-1-airflow-vpc-public-2a"
  }

  tags_all = {
    Name = "ariel-1-airflow-vpc-public-2a"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}

resource "aws_subnet" "tfer--subnet-002D-056e44f08860420d9" {
  assign_ipv6_address_on_creation                = "false"
  cidr_block                                     = "10.10.16.0/20"
  enable_dns64                                   = "false"
  enable_lni_at_device_index                     = "0"
  enable_resource_name_dns_a_record_on_launch    = "false"
  enable_resource_name_dns_aaaa_record_on_launch = "false"
  ipv6_native                                    = "false"
  map_customer_owned_ip_on_launch                = "false"
  map_public_ip_on_launch                        = "true"
  private_dns_hostname_type_on_launch            = "ip-name"

  tags = {
    Name = "ariel-1-airflow-vpc-public-2c"
  }

  tags_all = {
    Name = "ariel-1-airflow-vpc-public-2c"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}

resource "aws_subnet" "tfer--subnet-002D-05e740a676c96c988" {
  assign_ipv6_address_on_creation                = "false"
  cidr_block                                     = "10.10.192.0/20"
  enable_dns64                                   = "false"
  enable_lni_at_device_index                     = "0"
  enable_resource_name_dns_a_record_on_launch    = "false"
  enable_resource_name_dns_aaaa_record_on_launch = "false"
  ipv6_native                                    = "false"
  map_customer_owned_ip_on_launch                = "false"
  map_public_ip_on_launch                        = "false"
  private_dns_hostname_type_on_launch            = "ip-name"

  tags = {
    Name = "ariel-1-elasticache-2a"
  }

  tags_all = {
    Name = "ariel-1-elasticache-2a"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}

resource "aws_subnet" "tfer--subnet-002D-02580112e983f75fb" {
  assign_ipv6_address_on_creation                = "false"
  cidr_block                                     = "10.10.208.0/20"
  enable_dns64                                   = "false"
  enable_lni_at_device_index                     = "0"
  enable_resource_name_dns_a_record_on_launch    = "false"
  enable_resource_name_dns_aaaa_record_on_launch = "false"
  ipv6_native                                    = "false"
  map_customer_owned_ip_on_launch                = "false"
  map_public_ip_on_launch                        = "false"
  private_dns_hostname_type_on_launch            = "ip-name"

  tags = {
    Name = "ariel-1-elasticache-2c"
  }

  tags_all = {
    Name = "ariel-1-elasticache-2c"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}

resource "aws_subnet" "tfer--subnet-002D-0afe66517d65cd5df" {
  assign_ipv6_address_on_creation                = "false"
  cidr_block                                     = "10.10.160.0/20"
  enable_dns64                                   = "false"
  enable_lni_at_device_index                     = "0"
  enable_resource_name_dns_a_record_on_launch    = "false"
  enable_resource_name_dns_aaaa_record_on_launch = "false"
  ipv6_native                                    = "false"
  map_customer_owned_ip_on_launch                = "false"
  map_public_ip_on_launch                        = "false"
  private_dns_hostname_type_on_launch            = "ip-name"

  tags = {
    Name = "ariel-1-rds-2a"
  }

  tags_all = {
    Name = "ariel-1-rds-2a"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}

resource "aws_subnet" "tfer--subnet-002D-04dfa9ec82328de84" {
  assign_ipv6_address_on_creation                = "false"
  cidr_block                                     = "10.10.176.0/20"
  enable_dns64                                   = "false"
  enable_lni_at_device_index                     = "0"
  enable_resource_name_dns_a_record_on_launch    = "false"
  enable_resource_name_dns_aaaa_record_on_launch = "false"
  ipv6_native                                    = "false"
  map_customer_owned_ip_on_launch                = "false"
  map_public_ip_on_launch                        = "false"
  private_dns_hostname_type_on_launch            = "ip-name"

  tags = {
    Name = "ariel-1-rds-2c"
  }

  tags_all = {
    Name = "ariel-1-rds-2c"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}

resource "aws_subnet" "tfer--subnet-002D-0ca451f7b04533565" {
  assign_ipv6_address_on_creation                = "false"
  cidr_block                                     = "10.10.128.0/20"
  enable_dns64                                   = "false"
  enable_lni_at_device_index                     = "0"
  enable_resource_name_dns_a_record_on_launch    = "false"
  enable_resource_name_dns_aaaa_record_on_launch = "false"
  ipv6_native                                    = "false"
  map_customer_owned_ip_on_launch                = "false"
  map_public_ip_on_launch                        = "false"
  private_dns_hostname_type_on_launch            = "ip-name"

  tags = {
    Name = "ariel-1-airflow-vpc-private-2a"
  }

  tags_all = {
    Name = "ariel-1-airflow-vpc-private-2a"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}

resource "aws_subnet" "tfer--subnet-002D-06dab3c47ca2c6e97" {
  assign_ipv6_address_on_creation                = "false"
  cidr_block                                     = "10.10.144.0/20"
  enable_dns64                                   = "false"
  enable_lni_at_device_index                     = "0"
  enable_resource_name_dns_a_record_on_launch    = "false"
  enable_resource_name_dns_aaaa_record_on_launch = "false"
  ipv6_native                                    = "false"
  map_customer_owned_ip_on_launch                = "false"
  map_public_ip_on_launch                        = "false"
  private_dns_hostname_type_on_launch            = "ip-name"

  tags = {
    Name = "ariel-1-airflow-vpc-private-2c"
  }

  tags_all = {
    Name = "ariel-1-airflow-vpc-private-2c"
  }

  vpc_id = "${data.terraform_remote_state.local.outputs.aws_vpc_tfer--vpc-002D-08b42185f0b71ba2e_id}"
}
