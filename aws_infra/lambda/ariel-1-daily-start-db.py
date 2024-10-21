import json
import logging
import os
import time

import boto3

# 중단되어있던 특정 RDS, Redshift를 실행하는 함수

# EventBridge를 통해 KST 기준 매일 09:10에 Trigger 되게 설정

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
                "rds:StartDBInstance",
                "rds:DescribeDBInstances",
                "redshift:ResumeCluster",
                "redshift:DescribeClusters"
            ],
            "Resource": "*"
        }
    ]
}
"""


def lambda_handler(event, context):
    rds = boto3.client("rds")
    redshift = boto3.client("redshift")

    rds_instances = ["ariel-1-airflow-metadb", "ariel-1-production-db"]
    redshift_clusters = ["team-ariel-1-redshift-cluster"]

    try:
        # start RDS Instance
        for rds_instance in rds_instances:
            if (
                rds.describe_db_instances(DBInstanceIdentifier=rds_instance)[
                    "DBInstances"
                ][0]["DBInstanceStatus"]
                == "stopped"
            ):
                rds.start_db_instance(DBInstanceIdentifier=rds_instance)
                print(f"Started RDS instance: {rds_instance}")
            else:
                continue

    except Exception as e:
        logging.error(f"Failed to start RDS instances: {str(e)}")
        return {"statusCode": 500, "body": f"Failed to start RDS instances: {str(e)}"}

    try:
        # start Redshift Cluster
        for redshift_cluster in redshift_clusters:
            if (
                redshift.describe_clusters(ClusterIdentifier=redshift_cluster)[
                    "Clusters"
                ][0]["ClusterStatus"]
                == "paused"
            ):
                redshift.resume_cluster(ClusterIdentifier=redshift_cluster)
                print(f"Resumed Redshift cluster: {redshift_cluster}")
            else:
                continue

    except Exception as e:
        logging.error(f"Failed to resume Redshift clusters: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Failed to resume Redshift clusters: {str(e)}",
        }

    return {"statusCode": 200, "body": "Instances started successfully"}
