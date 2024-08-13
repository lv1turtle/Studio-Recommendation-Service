resource "aws_vpc" "tfer--vpc-002D-08b42185f0b71ba2e" {
  assign_generated_ipv6_cidr_block     = "false"
  cidr_block                           = "10.10.0.0/16"
  enable_dns_hostnames                 = "true"
  enable_dns_support                   = "true"
  enable_network_address_usage_metrics = "false"
  instance_tenancy                     = "default"
  ipv6_netmask_length                  = "0"

  tags = {
    Name = "ariel-1-airflow-vpc"
  }

  tags_all = {
    Name = "ariel-1-airflow-vpc"
  }
}