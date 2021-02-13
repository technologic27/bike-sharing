from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow import DAG
from datetime import timedelta, datetime

cron = '59 * * * *'
depends_on_past = False
pipeline_name = "test"

dag_args = {'owner': 'estherDawes',
            'depends_on_past': depends_on_past,
            'start_date': datetime(2020, 10, 1),
            'sla': timedelta(seconds=720),
            'retries': 1,
            'retry_delay': timedelta(seconds=20)}

dag = DAG(pipeline_name, default_args=dag_args, schedule_interval=cron)


t1 = BashOperator(task_id='file_ingestion_test',
                  depends_on_past=depends_on_past,
                  wait_for_downstream=False,
                  bash_command='python /usr/local/airflow/scripts/ingest.py',
                  retries=1,
                  dag=dag)

"""
t2 = PythonOperator(task_id='file_ingestion2',
                    dag=dag,
                    provide_context=True,
                    python_callable = test,
                    op_kwargs={'parameter1':test,
                    'parameter2':test})
"""

t1



