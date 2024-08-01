from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import time
from datetime import datetime
from datetime import timedelta
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import zipfile
import os


# vworld 부동산 중개업자(agent) 데이터를 받아오는 Task
def download_agent_data(download_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    # 다운로드 디렉토리 설정
    chrome_prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,  # 다운로드 대화상자 비활성화
        "download.directory_upgrade": True
    }
    options.add_experimental_option("prefs", chrome_prefs)
    
    search_input = '부동산중개업자'
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    vworld_url = f"https://www.vworld.kr/dtmk/dtmk_ntads_s002.do?searchBrmCode=&datIde=&searchFrm=&dsId=11&pageSize=10&pageUnit=10&listPageIndex=1&gidsCd=&searchKeyword=&searchOrganization=&dataSetSeq=11&svcCde=NA&searchTagList=&pageIndex=1&gidmCd=&sortType=00&datPageIndex=1&datPageSize=10&startDate={start_date}&endDate={end_date}&dsNm={search_input}"

    # 4444 포트에 있는 chromedriver를 호출 
    # ( seleniarm/standalone-chromium을 docker container에서 띄움 )
    remote_webdriver = 'remote_chromedriver'
    with webdriver.Remote(f'{remote_webdriver}:4444/wd/hub', options=options) as driver:
        driver.get(vworld_url)
        driver.implicitly_wait(3)
        time.sleep(10)
        
        # download_button을 불러와 이를 실행하여 download
        download_button = driver.find_elements(By.CLASS_NAME, 'bt.ico.down.bg.primary')[0]
        actions = ActionChains(driver).move_to_element(download_button)
        actions.perform()

        download_button.click()
        time.sleep(30)

# 파일의 columns 구성을 erd에 맞게 변경 후 덮어쓰기
def transform_columns(csv_file):
    df = pd.read_csv(csv_file, encoding="EUC-KR")

    df = df[["등록번호", "brkr_nm_encpt", "중개업자종별코드", "직위구분코드", "자격증번호"]]
    df.rename(columns={"등록번호":"registration_number", "brkr_nm_encpt":"agent_name", "중개업자종별코드":"agent_code", "직위구분코드":"position_code", "자격증번호":"certificate_number"}, inplace=True)

    df.to_csv(csv_file, encoding="utf-8", index=False, errors="replace")

# download한 파일을 압축 해제하여 s3에 적재하기 위해 경로를 전달
def get_csv_file_path(download_path):
    for filename in os.listdir(download_path):
        if filename.endswith('.zip'):
            zip_filepath = os.path.join(download_path, filename)
            extract_dir = os.path.join(download_path, f'extracted_{filename}')

            # ZIP 파일을 열고 압축 해제
            with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)  # ZIP 파일의 내용을 지정한 디렉토리에 압축 해제

            csv_filename = os.listdir(extract_dir)[0]
            csv_filepath = os.path.join(extract_dir, csv_filename)

            break

    paths = {
        "csv_filename":csv_filename,
        "csv_filepath":csv_filepath,
        "zip_filepath":zip_filepath,
        "extract_dir":extract_dir
    }

    return paths