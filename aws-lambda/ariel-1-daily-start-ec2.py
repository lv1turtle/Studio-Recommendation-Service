import boto3
import logging
# 중단되어 있던 특정 EC2를 실행하는 함수

# EventBridge를 통해 KST 기준 매일 09:20에 Trigger 되게 설정

# 필요한 IAM Policy
"""
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus",
            ],
            "Resource": "*"
        }
    ]
}
"""

region = 'ap-northeast-2' 
instances = ['i-0c40c86aa77af7b9d', 'i-07d478a96d7af433c', 'i-00b8613d9f2e92a67']
ec2 = boto3.client('ec2', region_name=region)

def lambda_handler(event, context):
    try : 
        ec2.start_instances(InstanceIds=instances)
        print('start your instances: ' + str(instances))
    except Exception as e:
        logging.error(f"Failed to start EC2 instances: {str(e)}")
        return {'statusCode': 500, 'body': f'Failed to start EC2 instances: {str(e)}'}