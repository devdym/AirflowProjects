from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from datetime import datetime
from gemeni.GunLinkLogs import *
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator

glhost = Variable.get("GLserver")

args = {
    'owner': 'Airflow',
    'start_date': datetime.now(),
    'provide_context': True,
}

dag = DAG(
    dag_id='copyGunLinkLog',
    default_args=args,
    schedule_interval='* * * * *',
    tags=['gemeni'],
    catchup=False
)

connect = BranchPythonOperator(task_id='connect',
                               python_callable=connect_to_server,
                               provide_context=True,
                               dag=dag)

script_exec = BashOperator(task_id='generate_stat_and_log_files',
                    bash_command='ssh display@' + glhost + ' get_line_log -l',
                    # xcom_push=True,
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
get_missing_files >> [script_exec, finish]
script_exec >> copy
copy >> finish
