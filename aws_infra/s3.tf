resource "aws_s3_bucket" "team-ariel-1-bucket" {
    bucket = "team-ariel-1-bucket"
    acl    = "private"
}

resource "aws_s3_bucket" "team-ariel-1-dags" {
    bucket = "team-ariel-1-dags"
    acl    = "private"
}
