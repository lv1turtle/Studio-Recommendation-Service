# 자취를 시작하는 분들을 위한 원룸 추천 웹 서비스
![15](https://github.com/user-attachments/assets/54e5e2bd-0c2d-494b-b9af-fb7219eb2da8)

## 팀 소개
| 이름 | 역할 | github |
| --- | --- | --- |
| 석형원 | 주제 선정, AWS Infra 설계 및 구축, Airflow 서버 개발, CI/CD | https://github.com/lv1turtle |
| 서상민 | ERD 설계, 데이터 전처리 및 ELT DAG 작성, 대시보드 제작 | https://github.com/ss721229 |
| 이정근 | 다방 데이터 수집 DAG 작성, 웹 서비스 풀스택 개발 | https://github.com/nooreong2 |
| 김서연 | 직방, 부동산 중개업자 데이터 수집 DAG 작성, 머신러닝 모델 학습 및 예측 DAG 작성 | https://github.com/seoyeon83 |

## 프로젝트 소개
> **기존 부동산 서비스** : [다방](https://www.dabangapp.com/), [직방](https://www.zigbang.com/)

- 여러 부동산 플랫폼의 데이터(다방, 직방)를 통합하여 더 많은 선택지 제공 및 최적의 매물을 추천해주는 웹 서비스입니다.
- 사용자의 요구와 조건을 반영하여 매물 추천 알고리즘을 설계하여 맞춤형 매물 추천 시스템을 구축하였습니다.
- 매물을 쉽고 빠르게 찾을 수 있게 직관적인 웹 서비스의 형태로 제작했습니다.
- 인공지능을 활용한 매물 추천 시스템을 도입하여 신뢰성 높은 추천 결과도 제공합니다.

### 개발 환경
---
| 분류 | 활용 기술 및 프레임워크 |
| --- | --- |
| Programming | Python, SQL |
| Cloud Service | AWS (Terraform) |
| Data Storage | AWS S3, AWS Redshift, AWS RDS(MySQL, Postgres) |
| Data Processing | Apache Airflow 2.5.1, AWS Glue |
| Web Service | React, Django, Nginx, Recoil |
| AI | Python(scikit-learn) |
| Visualization | Metabase |
| Collaboration | Github, Notion, Slack, Gather Town |

## How to use
### Docker 기반 Airflow 실행
```bash
docker build . --tag extending_airflow:2.5.1

docker compose -f docker-compose-main.yaml up airflow-init

docker compose -f docker-compose-main.yaml up -d
```

### 독립된 환경에서 Airflow worker만 실행 - scale out
```bash
docker build . --tag extending_airflow:2.5.1
docker compose -f docker-compose-worker.yaml up -d
```

### Webserver 실행 방법 
- FrontEnd
    - **requirements install** : `npm install`
    - **local debug mode** : `npm start`
    - **make build file** : `npm run build`
- BackEnd
    - **server start** : `python3 manage.py runserver`
    - **API**
        1. `localhost:8000/swagger` 접속
        2. swagger를 통해 필요 reqeust와 response를 확인 가능
    - **database**
        - 아래 다음 명령어를 수행
            1. `python3 manage.py makemigrations`
            2. `python3 manage.py migrate`


## Data Pipeline
![data pipeline jpg](https://github.com/user-attachments/assets/b2bb6ff8-f08f-47d6-9d22-08454ca698a6)

## INFRA
### AWS Architecutre
![aws architecture1 jpg](https://github.com/user-attachments/assets/38341668-0d7d-4f30-8050-cd482edc1024)

### AWS EC2 Auto Scaling Group - Airflow worker
![autoscaling jpg](https://github.com/user-attachments/assets/cc0b9075-70c0-464d-ac9f-62addc4e6c8e)

## ERD
![스크린샷 2024-08-20 오후 4 22 58](https://github.com/user-attachments/assets/855a205d-5b73-4175-b722-5dbdf3d7b33f)

https://www.erdcloud.com/d/uaBgpDCXxH6t8GXkL


## ETL, ELT
### ETL
![스크린샷 2024-08-20 오후 4 28 54](https://github.com/user-attachments/assets/378efe70-cfe6-49f3-a435-d68024903bb7)

### ELT
![스크린샷 2024-08-20 오후 4 29 53](https://github.com/user-attachments/assets/55b4dced-19bd-44bf-afc2-a616ba887cb8)

## 매물 추천 알고리즘
- 매물 추천 알고리즘
    - 편의 시설 및 방향 점수:
      - 산정 방법 :
        1. 각 매물에 따라 아래 점수표대로 점수를 부여 후 총합 점수를 구한다.
        2. 이를 기준으로 Rank로 오름차순으로 순위를 매긴다.
        3. 해당 Rank 순위를 편의 시설 및 방향 점수라 한다.

      - 점수표 :
        - 대형마트 유무 : 대형마트가 있으면 3점, 없으면 0점
        - 음식점 : 없으면 0, 5개 이하(1점), 6개~15개이하(2점), 15개초과(3점)
        - 편의점 거리 : 100미터 대(3점), 300미터 (2점), 500 (1점), 그 외 0점
        - 카페 거리 : 100미터 대(3점), 300미터 (2점), 500 (1점), 그 외 0점
        - 지하철 유무 :  있으면 3점, 없으면 0점
        - 병원 : 없으면 0, 8개(1점), 8개~20개(2점), 20개 이상(3점)
        - 방 방향 : 남쪽이 포함되면 3점, 남이 포함되지 않고 서나 북이 포함되면 -3점, 그외는 0점

    - 가격 점수 :
      - 산정 방법 :
        1. 각 매물에 따라 아래 월 지출비를 구한다.
        2. 이를 기준으로 Rank로 내림차순으로 순위를 매긴다.
        3. 해당 Rank 순위를 가격 점수라 한다.

      - 월 지출비 : 보증금 *  1/20 * 1/12 + 월세
        - 보증금을 연이자 5%로 월별 가치 계산

    - 최종 추천 알고리즘 : 3*( 가격 점수 ) + 2*( 편의시설 및 방향 점수 )

## ML
- Dataset
    - Y(target): 거래 완료 여부
        - 거래 완료 매물(0)
        - 미거래 매물(1) ( `updateAt` 기준 30일 초과시 미거래 매물 )
    - X(features)
        - 층 높이: 범주형(옥탑, 반지하, 저, 중, 고)
        - 면적: $M^2$ 단위 실수형
        - 보증금: 정수형
        - 월세: 정수형
        - 관리비: 실수형
        - 지역구: 범주형(강남구, 감동구, 등 …)
        - 방향: 범주형(동, 서, 남, 북, 북동, 남동, 북서, 남서)
        - 주변 편의 시설 종류 개수: 정수형

- 활용 모델: RandomForest
    - 결과적으로 0, 1을 분류해야 하고 입력 변수에 카테고리형 데이터가 존재해 트리 기반의 앙상블 모델인 RandomForest 선정

![스크린샷 2024-08-20 오후 4 46 04](https://github.com/user-attachments/assets/95f48e68-4937-497f-a060-6b802c6e93fa)

## 대시보드
![스크린샷 2024-08-20 오후 4 39 19](https://github.com/user-attachments/assets/37b60f74-e0e7-4c11-9060-69a2b5e0561b)

![스크린샷 2024-08-20 오후 4 40 01](https://github.com/user-attachments/assets/2215d4cc-d21d-4ca4-81af-d2cbee185461)


## WebService
### Architecture
![webservice](https://github.com/user-attachments/assets/0e4cdb37-5e5b-4e0c-a662-bee13646ff7a)

- FrontEnd Framework로 React를 사용
- BackEnd Framework로 Django를 사용
- DataBase는 AWS RDS 사용
- NaverMap을 활용하여 편의시설 정보 제공
### 1. 메인 페이지

![15](https://github.com/user-attachments/assets/54e5e2bd-0c2d-494b-b9af-fb7219eb2da8)

- 사용자가 편리하고 쉽게 서비스에 접근할 수 있도록 UI/UX 설계
- 시작하기 버튼을 통해 서비스를 쉽게 접근 가능

### 2. 주소 검색 페이지
        
<img width="1439" alt="addresspage" src="https://github.com/user-attachments/assets/013fdb95-edc6-4c7b-a211-3f52215f5aa3">
        
- 입력창을 통해 살고 싶은 동네를 입력 받도록 설계, 이후 입력 받은 동네는 Parameter로서 최종 API 호출에 사용
- Recoil 라이브러리를 활용하여 동네 입력값을 저장
- 입력창 하단에 tip을 추가하여 사용자에게 입력 예시를 제공, 사용자 편의성 증대

### 3. 보증금 및 월세 입력 페이지
        
<img width="1440" alt="cost" src="https://github.com/user-attachments/assets/c2d2d035-0808-4def-9e64-e6c783213465">
        
- 사용자가 방을 구하기 위해 정한 예산을 입력하는 페이지
- 사전에 데이터 EDA를 통해 보증금을 최대 3억, 월세를 200만원까지 설정
- react-slider를 사용하여 사용자가 액티브하게 값을 설정할 수 있음

### 4. 편의 시설 입력 페이지
        
<img width="1439" alt="facility" src="https://github.com/user-attachments/assets/b6a33f40-dc78-492b-9777-57a42a1d10f1">
        
- 주변에 있었으면 하는 편의시설에 대하여 입력 받는 페이지
- API 호출에서 배열로서 전달되며, 해당 편의시설이 주변에 존재하는 매물만을 반영하게 된다.

### 5. 반지하, 옥탑방 제외 입력 페이지
        
<img width="1438" alt="floor" src="https://github.com/user-attachments/assets/43c2cc9b-eeed-44d1-b6eb-a1629b250076">
        
- 사용자가 옥탑방이나 반지하를 원하지 않는 경우 제외하여 결과를 확인할 수 있다.

### 6. 조건에 맞는 데이터를 보여주는 정보 제공 페이지
        
![info](https://github.com/user-attachments/assets/0f55bfd0-c608-4b89-b141-dc133e377789)
        
- 검색된 데이터들의 정보를 순위 별로 확인할 수 있는 페이지
- 왼쪽에는 설정한 조건들을 확인할 수 있다.
- 매물의 사진, 보증금, 월세, 주소 및 상세 정보, NaverMap을 통하여 주변 시설등을 확인할 수 있다.

### Webservice 관련 문의 
- email : wjdrms0402@gmail.com
- github : nooreong2