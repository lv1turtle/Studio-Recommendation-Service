FROM apache/airflow:2.5.1
COPY requirements.txt /requirements.txt
RUN pip install --user --upgrade pip
RUN pip install -r /requirements.txt

# docker build . --tag extending_airflow:2.5.1