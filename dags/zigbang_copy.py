from datetime import datetime
from airflow.models import Variable

from airflow import DAG
from airflow.operators.python import PythonOperator


def copy_s3_to_redshift(schema, table, s3_url, iam_s3_role):
    from dags.copy_zigbang_initial_data import copy_zigbang_initial_data

    copy_zigbang_initial_data(schema, table, s3_url, iam_s3_role)



with DAG('zigbang_copy_to_redshift',
         schedule_interval='0 1 * * *',
        start_date=datetime(2024, 7, 1),
        catchup=False
        ) as dag:

    copy_s3_to_redshift = PythonOperator(
        task_id='copy_s3_to_redshift',
        python_callable=copy_s3_to_redshift,
        op_kwargs={
                    'schema': 'rawdata',
                    'table': 'zigbang',
                    's3_url': Variable.get("s3_zigbang_url"),
                    'iam_s3_role': Variable.get("iam_s3_role")
                }
    )


copy_s3_to_redshift