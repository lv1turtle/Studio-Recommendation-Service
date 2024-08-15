from __future__ import print_function

import json, boto3
import time
import logging
from botocore.exceptions import ClientError

"""
( 이전 계획 )
# AutoScaleGroup으로부터 미리 생성해둔 시작 템플릿을 기반으로 인스턴스가 생성되면 SNS 알림이 발생
# 이 SNS 알림으로 Trigger되는 Lambda 함수로,
# 미리 생성해둔 AMI 이미지를 알림의 주체가 되는 인스턴스의 루트 볼륨과 Replace

# 여기서 AMI 이미지는 Worker가 바로 동작할 수 있는 인스턴스를 저장한 이미지

#-------------------------------------------------------------------------------

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    # AutoScaling 이벤트 알림에서 EC2 Instace ID를 추출
    message = event['Records'][0]['Sns']['Message']
    autoscalingInfo = json.loads(message)
    ec2InstanceId = autoscalingInfo['EC2InstanceId']
    
    # 루트 볼륨을 미리 생성해둔 AMI 이미지로 교체
    ec2 = boto3.client('ec2', region_name=region)
    try :
        response_ami = ec2.create_replace_root_volume_task(
            InstanceId=ec2InstanceId,
            ImageId=amiImageId,
            DeleteReplacedRootVolume=True
        )
        
    except Exception as e:
        logging.error(f"Error replacing root volume to EC2 instance: {str(e)}")
        return {'statusCode': 500, 'body': f'Failed_replace : {str(e)}'}
    
    # 교체가 진행되는 5분을 기다림
    time.sleep(300)
    print(response_ami)
    
    # dags를 갱신하는 lambda 함수를 호출
    lambdaCli = boto3.client('lambda')
    try:
        response_lambda = lambdaCli.invoke(
            FunctionName='ariel-1-deploy-dags'
        )
        print(response_lambda['Payload'].read())
        
    except Exception as e:
        logging.error(f"Error updating dags to EC2 instance: {str(e)}")
        return {'statusCode': 500, 'body': f'Failed_update : {str(e)}'}
    
    return {
        'statusCode': 200,
        'body': 'Auto scaling process completed.'
    }
    
-> 처음부터 시작템플릿에 AMI를 설정할 수 있다는 것을 알게되어 계획을 수정
#-------------------------------------------------------------------------------
"""

# AutoScaleGroup으로부터 미리 생성해둔 시작 템플릿을 기반으로 인스턴스가 생성되면 SNS 알림이 발생
# ( 이때, 시작 템플릿에는 docker-compose의 형태로 worker를 바로 실행시킬 수 있는 세팅이 완료되어있음 )
# 이 SNS 알림으로 Trigger되는 Lambda 함수로,
# AWS CLI와 SSM을 통해 인스턴스에 접근하여 S3에 있는 dags를 배포 후 worker를 실행하는 명령을 내림 


# 필요한 IAM Policy
"""
- AmazonEC2FullAccess

- AWSLambdaBasicExecutionRole

- AmazonSSMFullAccess
"""

ssm = boto3.client('ssm')
AWS_S3_BUCKET_NAME = 'team-ariel-1-dags'
EC2_PATH = '/home/ubuntu/airflow/dags'

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    # AutoScaling 이벤트 알림에서 EC2 Instace ID를 추출
    message = event['Records'][0]['Sns']['Message']
    autoscalingInfo = json.loads(message)
    ec2InstanceId = autoscalingInfo['EC2InstanceId']
    
    # 인스턴스가 실행되는데 넉넉하게 5분 대기
    time.sleep(300)
    
    try :
        response = ssm.send_command(
            InstanceIds = [ec2InstanceId],
            # shell 명령 사용
            DocumentName="AWS-RunShellScript",
            Parameters={
                'commands': [
                    # S3에 적재된 dags 갱신 & celery worker 실행
                    f'aws s3 sync --delete s3://{AWS_S3_BUCKET_NAME} {EC2_PATH} && docker compose -f /home/ubuntu/airflow/docker-compose-worker.yaml up -d'
                ]
            }
        )
        print(response)
            
    except ClientError as e:
        print(f"[ERROR] failed to start worker : {str(e)}")
        return {'statusCode': 500, 'body': f'failed to start worker : {str(e)}'}
    
    return {
        'statusCode': 200,
        'body': 'Auto scaling process completed.'
    }