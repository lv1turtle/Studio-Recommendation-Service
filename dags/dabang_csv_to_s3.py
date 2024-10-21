from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


def fetch_data(**kwargs):
    import extract_dabang_v2

    output_file = extract_dabang_v2.get_data_all()

    kwargs["ti"].xcom_push(key="output_file", value=output_file)


def upload_to_s3(**kwargs):
    hook = S3Hook("s3_conn")

    # XCom에서 파일 경로 가져옴
    ti = kwargs["ti"]
    filename = ti.xcom_pull(task_ids="fetch_data", key="output_file")

    if not filename:
        raise ValueError("No file found to upload.")

    # S3로 파일 업로드
    hook.load_file(
        filename=filename,
        key=kwargs["key"],
        bucket_name=kwargs["bucket_name"],
        replace=True,
    )


with DAG(
    "dabang_upload_to_s3",
    schedule="0 3 * * *",
    start_date=datetime(2024, 7, 1),
    catchup=False,
) as dag:

    fetch = PythonOperator(
        task_id="fetch_data",
        python_callable=fetch_data,
    )

    save_upload = PythonOperator(
        task_id="save_upload",
        python_callable=upload_to_s3,
        op_kwargs={
            "key": "dabang/save/{{ ds }}/dabang_{{ ds }}.parquet",
            "bucket_name": "team-ariel-1-bucket",
        },
    )

    overwrite_upload = PythonOperator(
        task_id="overwrite_upload",
        python_callable=upload_to_s3,
        op_kwargs={
            "key": "dabang/overwrite/dabang.parquet",
            "bucket_name": "team-ariel-1-bucket",
        },
    )

fetch >> overwrite_upload >> save_upload
