resource "aws_security_group" "tfer--ariel-002D-1-002D-ariflow-002D-sg_sg-002D-06580bff68fc46b84" {
  description = "Security group of airflow"

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "22"
    protocol    = "tcp"
    self        = "false"
    to_port     = "22"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "5555"
    protocol    = "tcp"
    self        = "false"
    to_port     = "5555"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "8080"
    protocol    = "tcp"
    self        = "false"
    to_port     = "8080"
  }

  name   = "ariel-1-ariflow-sg"
  vpc_id = "vpc-08b42185f0b71ba2e"
}

resource "aws_security_group" "tfer--ariel-002D-1-002D-bastion-002D-host_sg-002D-01f788440f62ba867" {
  description = "Security group for Bastion host"

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    cidr_blocks = ["117.111.10.1/32", "122.36.197.126/32", "13.73.34.239/32", "13.73.53.230/32", "211.36.147.98/32", "211.62.129.199/32", "221.145.230.60/32", "23.102.140.63/32", "40.84.171.131/32", "61.39.229.76/32", "61.43.120.138/32", "74.249.23.176/32"]
    from_port   = "22"
    protocol    = "tcp"
    self        = "false"
    to_port     = "22"
  }

  ingress {
    cidr_blocks = ["211.62.129.199/32", "61.39.229.76/32"]
    from_port   = "3000"
    protocol    = "tcp"
    self        = "false"
    to_port     = "3000"
  }

  name   = "ariel-1-bastion-host"
  vpc_id = "vpc-08b42185f0b71ba2e"
}

resource "aws_security_group" "tfer--ariel-002D-1-002D-production-002D-db-002D-sg_sg-002D-06f485ac5aa3b6276" {
  description = "Created by RDS management console"

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "3306"
    protocol    = "tcp"
    self        = "false"
    to_port     = "3306"
  }

  name   = "ariel-1-production-db-sg"
  vpc_id = "vpc-08b42185f0b71ba2e"
}

resource "aws_security_group" "tfer--ariel-002D-1-002D-redis-002D-sg_sg-002D-01a6e35ebc4d1ea42" {
  description = "for elasticache-redis"

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "tcp"
    self        = "false"
    to_port     = "65535"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "6379"
    protocol    = "tcp"
    self        = "false"
    to_port     = "6379"
  }

  name   = "ariel-1-redis-sg"
  vpc_id = "vpc-08b42185f0b71ba2e"
}

resource "aws_security_group" "tfer--ariel-002D-1-002D-web-002D-ui-002D-alb-002D-sg_sg-002D-0d2c0bd7dbe053c4a" {
  description = "security group - airflow web ui alb"

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    cidr_blocks = ["122.36.197.126/32", "211.62.129.199/32", "221.145.230.60/32", "61.39.229.76/32"]
    from_port   = "80"
    protocol    = "tcp"
    self        = "false"
    to_port     = "80"
  }

  ingress {
    cidr_blocks = ["122.36.197.126/32", "211.62.129.199/32", "221.145.230.60/32", "61.39.229.76/32"]
    from_port   = "81"
    protocol    = "tcp"
    self        = "false"
    to_port     = "81"
  }

  name   = "ariel-1-web-ui-alb-sg"
  vpc_id = "vpc-08b42185f0b71ba2e"
}

resource "aws_security_group" "tfer--ariel-002D-1-002D-webserver-002D-alb-002D-sg_sg-002D-0f1f95dbcc3d48098" {
  description = "for ariel-1-webserver-alb"

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  name   = "ariel-1-webserver-alb-sg"
  vpc_id = "vpc-08b42185f0b71ba2e"
}

resource "aws_security_group" "tfer--ec2-002D-rds-002D-4_sg-002D-00c55e446a6a5917d" {
  description = "Security group attached to instances to securely connect to ariel-1-airflow-metadb. Modification could lead to connection loss."

  egress {
    description     = "Rule to allow connections to ariel-1-airflow-metadb from any instances this security group is attached to"
    from_port       = "5432"
    protocol        = "tcp"
    security_groups = ["${data.terraform_remote_state.local.outputs.aws_security_group_tfer--rds-002D-ec2-002D-4_sg-002D-090e7b90adc15277a_id}"]
    self            = "false"
    to_port         = "5432"
  }

  name   = "ec2-rds-4"
  vpc_id = "vpc-08b42185f0b71ba2e"
}

resource "aws_security_group" "tfer--ec2-002D-rds-002D-7_sg-002D-0b68b99efa1240a31" {
  description = "Security group attached to instances to securely connect to ariel-1-production-db. Modification could lead to connection loss."

  egress {
    description     = "Rule to allow connections to ariel-1-production-db from any instances this security group is attached to"
    from_port       = "3306"
    protocol        = "tcp"
    security_groups = ["${data.terraform_remote_state.local.outputs.aws_security_group_tfer--rds-002D-ec2-002D-7_sg-002D-0d4bba7fb1a773ba3_id}"]
    self            = "false"
    to_port         = "3306"
  }

  name   = "ec2-rds-7"
  vpc_id = "vpc-08b42185f0b71ba2e"
}

resource "aws_security_group" "tfer--rds-002D-ec2-002D-4_sg-002D-090e7b90adc15277a" {
  description = "Security group attached to ariel-1-airflow-metadb to allow EC2 instances with specific security groups attached to connect to the database. Modification could lead to connection loss."

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "5432"
    protocol    = "tcp"
    self        = "false"
    to_port     = "5432"
  }

  ingress {
    description     = "Rule to allow connections from EC2 instances with sg-00c55e446a6a5917d attached"
    from_port       = "5432"
    protocol        = "tcp"
    security_groups = ["${data.terraform_remote_state.local.outputs.aws_security_group_tfer--ec2-002D-rds-002D-4_sg-002D-00c55e446a6a5917d_id}"]
    self            = "false"
    to_port         = "5432"
  }

  name   = "rds-ec2-4"
  vpc_id = "vpc-08b42185f0b71ba2e"
}

resource "aws_security_group" "tfer--rds-002D-ec2-002D-7_sg-002D-0d4bba7fb1a773ba3" {
  description = "Security group attached to ariel-1-production-db to allow EC2 instances with specific security groups attached to connect to the database. Modification could lead to connection loss."

  ingress {
    description     = "Rule to allow connections from EC2 instances with sg-0b68b99efa1240a31 attached"
    from_port       = "3306"
    protocol        = "tcp"
    security_groups = ["${data.terraform_remote_state.local.outputs.aws_security_group_tfer--ec2-002D-rds-002D-7_sg-002D-0b68b99efa1240a31_id}"]
    self            = "false"
    to_port         = "3306"
  }

  name   = "rds-ec2-7"
  vpc_id = "vpc-08b42185f0b71ba2e"
}