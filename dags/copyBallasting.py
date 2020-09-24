from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from datetime import datetime
from gemeni.GunLinkLogs import *


args = {
    'owner': 'Airflow',
    'start_date': datetime.now(),
    'provide_context': True,
}

dag = DAG(
    dag_id='copyGunLinkLog',
    default_args=args,
    schedule_interval='* * * * *',
    tags=['gemeni']
)

connect = BranchPythonOperator(task_id='connect',
                               python_callable=connect_to_server,
                               provide_context=True,
                               dag=dag)

list_source_folder = PythonOperator(task_id='read_source',
                             python_callable=read_source_folder,
                             provide_context=True,
                             dag=dag)

list_dist_folder = PythonOperator(task_id='read_dist',
                             python_callable=read_dist_folder,
                             provide_context=True,
                             dag=dag)

get_missing_files = BranchPythonOperator(task_id='get_missing_files',
                                   python_callable=compare_log_files,
                                   provide_context=True,
                                   dag=dag)

copy = PythonOperator(task_id='copy_files',
                      python_callable=copy,
                      provide_context=True,
                      dag=dag)

finish = DummyOperator(task_id='finish',
                       dag=dag)

connect >> [list_source_folder, finish]
list_source_folder >> list_dist_folder
list_dist_folder >> get_missing_files
get_missing_files >> [copy, finish]
copy >> finish
