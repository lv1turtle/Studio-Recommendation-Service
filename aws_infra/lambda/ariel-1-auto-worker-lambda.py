from __future__ import print_function

import json, boto3
import time
import logging
from botocore.exceptions import ClientError

# AutoScaleGroup으로부터 인스턴스가 생성되면 SNS 알림이 발생
# 이 SNS 알림으로 Trigger되는 Lambda 함수로,
# 미리 생성해둔 AMI 이미지를 알림의 주체가 되는 인스턴스의 루트 볼륨과 Replace

# 여기서 AMI 이미지는 Worker가 바로 동작할 수 있는 인스턴스를 저장한 이미지

# 필요한 IAM Policy
"""
- AmazonEC2FullAccess

- AWSLambdaBasicExecutionRole

- AWSLambdaRole
"""


region = 'ap-northeast-2'
# 교체할 AMI 이미지
amiImageId = 'ami-055b9b4f978f0e05e'

# 루트 볼륨을 교체하는데 시간이 오래걸리니 제한 시간을 넉넉하게 둘 것!
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