import boto3
from botocore.exceptions import ClientError

# Github Actions를 통해 Trigger 되는 함수
# SSM을 통해 Airflow가 동작하는 EC2 (AutoScaleGroup 포함)에 접근
# AWS CLI 명령을 통해 S3에 저장된 dags 버킷의 내용을 sync

# 필요한 IAM Policy
"""
- AmazonEC2FullAccess

- AmazonSSMFullAccess

- AutoScalingFullAccess

- AWSLambdaBasicExecutionRole
"""

region = "ap-northeast-2"
instance_ids = ["i-07d478a96d7af433c"]
ec2 = boto3.client("ec2", region_name=region)
as_client = boto3.client("autoscaling", region_name=region)
ssm = boto3.client("ssm")
AWS_S3_BUCKET_NAME = "team-ariel-1-dags"
EC2_PATH = "/home/ubuntu/airflow/dags"


def lambda_handler(event, context):
    as_groups = as_client.describe_auto_scaling_groups(
        AutoScalingGroupNames=["ariel-1-auto-worker"]
    )

    for i in as_groups["AutoScalingGroups"]:
        for k in i["Instances"]:
            instance_ids.append(k["InstanceId"])
            print(k["InstanceId"])

    print(instance_ids)
    for instance_id in instance_ids:
        try:
            response = ssm.send_command(
                InstanceIds=[instance_id],
                # shell 명령 사용
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": [
                        f"aws s3 sync --delete s3://{AWS_S3_BUCKET_NAME} {EC2_PATH}"
                    ]
                },
            )

        except ClientError as e:
            print(
                f"[ERROR] Error transferring file to EC2 instance {instance_id}: {str(e)}"
            )
            return {"statusCode": 500, "body": f"Failed to deploy : {str(e)}"}

    return {"statusCode": 200, "body": "deploy process completed."}
