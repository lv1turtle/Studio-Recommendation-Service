resource "aws_instance" "ariel-1-bastion-host" {
    ami                         = "ami-056a29f2eddc40520"
    availability_zone           = "ap-northeast-2a"
    ebs_optimized               = false
    instance_type               = "t2.micro"
    monitoring                  = false
    key_name                    = "team-ariel-1-private-key"
    subnet_id                   = "subnet-04725e6917247af69"
    vpc_security_group_ids      = ["sg-01f788440f62ba867"]
    associate_public_ip_address = true
    source_dest_check           = true

    root_block_device {
        volume_type           = "gp2"
        volume_size           = 8
        delete_on_termination = true
    }

    tags {
        "Name" = "ariel-1-bastion-host"
    }
}

resource "aws_instance" "ariel-1-airflow-server" {
    ami                         = "ami-056a29f2eddc40520"
    availability_zone           = "ap-northeast-2a"
    ebs_optimized               = true
    instance_type               = "t3.medium"
    monitoring                  = false
    key_name                    = "team-ariel-1-private-key"
    subnet_id                   = "subnet-0ca451f7b04533565"
    vpc_security_group_ids      = ["sg-00c55e446a6a5917d", "sg-06580bff68fc46b84", "sg-01f788440f62ba867"]
    associate_public_ip_address = false
    source_dest_check           = true

    root_block_device {
        volume_type           = "gp2"
        volume_size           = 40
        delete_on_termination = true
    }

    tags {
        "Name" = "ariel-1-airflow-server"
    }
}

resource "aws_instance" "ariel-1-web-server" {
    ami                         = "ami-056a29f2eddc40520"
    availability_zone           = "ap-northeast-2a"
    ebs_optimized               = true
    instance_type               = "t3.medium"
    monitoring                  = false
    key_name                    = "team-ariel-1-webserver-key"
    subnet_id                   = "subnet-04725e6917247af69"
    vpc_security_group_ids      = ["sg-0b68b99efa1240a31", "sg-01f788440f62ba867"]
    associate_public_ip_address = true
    source_dest_check           = true

    root_block_device {
        volume_type           = "gp2"
        volume_size           = 30
        delete_on_termination = true
    }

    tags {
        "Name" = "ariel-1-web-server"
    }
}
