resource "aws_db_instance" "ariel-1-airflow-metadb" {
    identifier                = "ariel-1-airflow-metadb"
    allocated_storage         = 400
    storage_type              = "io2"
    engine                    = "postgres"
    engine_version            = "16.3"
    instance_class            = "db.t3.small"
    username                  = "postgres"
    password                  = "xxxxxxxx"
    port                      = 5432
    publicly_accessible       = false
    availability_zone         = "ap-northeast-2a"
    vpc_security_group_ids    = ["sg-06580bff68fc46b84", "sg-090e7b90adc15277a"]
    db_subnet_group_name      = "ariel-1-rds-subnet-group"
    parameter_group_name      = "default.postgres16"
    multi_az                  = false
}
resource "aws_db_instance" "ariel-1-production-db" {
    identifier                = "ariel-1-production-db"
    allocated_storage         = 200
    storage_type              = "gp3"
    engine                    = "mysql"
    engine_version            = "8.0.35"
    instance_class            = "db.t3.small"
    username                  = "admin"
    password                  = "xxxxxxxx"
    port                      = 3306
    publicly_accessible       = false
    availability_zone         = "ap-northeast-2a"
    vpc_security_group_ids    = ["sg-0d4bba7fb1a773ba3", "sg-06f485ac5aa3b6276"]
    db_subnet_group_name      = "ariel-1-production-db-subnet-group"
    parameter_group_name      = "ariel-1-local-infile"
    multi_az                  = false
}
