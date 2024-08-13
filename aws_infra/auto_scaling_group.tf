resource "aws_launch_template" "ariel-1-worker" {
    name_prefix = "ariel-1-worker"
    image_id = "ami-056a29f2eddc40520"
    instance_type = "t3.small"
}

resource "aws_autoscaling_group" "ariel-1-auto-worker" {
    desired_capacity          = 1
    health_check_grace_period = 300
    health_check_type         = "EC2"
    launch_template{
        id = lt-004522ddf59af2762
        name = ariel-1-worker
        version = "$Latest"
    }
    max_size                  = 3
    min_size                  = 1
    name                      = "ariel-1-auto-worker"
    vpc_zone_identifier       = ["subnet-06dab3c47ca2c6e97", "subnet-0ca451f7b04533565"]
    tag {
        key   = "Name"
        value = "ariel-1-auto-worker"
        propagate_at_launch = true
    }
}

resource "aws_cloudwatch_metric_alarm" "ariel-1-auto-worker-cpu-high-alarm" {
    alarm_name          = "ariel-1-auto-worker-cpu-high-alarm"
    comparison_operator = "GreaterThanThreshold"
    evaluation_periods  = "1"
    metric_name         = "CPUUtilization"
    namespace           = "AWS/EC2"
    period              = "300"
    statistic           = "Average"
    threshold           = "40.0"
    alarm_description   = ""
    alarm_actions       = ["arn:aws:autoscaling:ap-northeast-2:862327261051:scalingPolicy:831c0880-e733-4e6f-9a18-99c7aebd27d8:autoScalingGroupName/ariel-1-auto-worker:policyName/ariel-1-auto-worker-scale-out"]
    dimensions {
        AutoScalingGroupName = "ariel-1-auto-worker"
    }
}

resource "aws_cloudwatch_metric_alarm" "ariel-1-auto-worker-cpu-low-alarm" {
    alarm_name          = "ariel-1-auto-worker-cpu-low-alarm"
    comparison_operator = "LessThanThreshold"
    evaluation_periods  = "1"
    metric_name         = "CPUUtilization"
    namespace           = "AWS/EC2"
    period              = "900"
    statistic           = "Average"
    threshold           = "5.0"
    alarm_description   = ""
    alarm_actions       = ["arn:aws:autoscaling:ap-northeast-2:862327261051:scalingPolicy:83c17ada-ec61-4de0-803c-dd9e4cff92b3:autoScalingGroupName/ariel-1-auto-worker:policyName/ariel-1-auto-worker-scale-in"]
    dimensions {
        AutoScalingGroupName = "ariel-1-auto-worker"
    }
}