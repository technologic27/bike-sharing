FROM puckel/docker-airflow

USER root
WORKDIR /usr/local/airflow
COPY requirements.txt .
RUN pip install -r requirements.txt
