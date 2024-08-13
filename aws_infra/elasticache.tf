resource "aws_elasticache_cluster" "ariel-1-redis-broker" {
    cluster_id             = "ariel-1-redis-broker"
    engine                 = "redis"
    engine_version         = "7.1.0"
    node_type              = "cache.t3.micro"
    num_cache_nodes        = 1
    port                   = 6379
    subnet_group_name      = "subnet-ariel-1-redis"
    security_group_ids     = ["sg-01a6e35ebc4d1ea42"]
}