from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from datetime import datetime
from gemeni.ballasting import *
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago


args = {
    'owner': 'air',
    'start_date': datetime.now(),
    'provide_context': True,
    'start_date': days_ago(2),
}

dag = DAG(
    dag_id='copyBallastingLogs',
    default_args=args,
    schedule_interval='* * * * *',
    tags=['gemeni'],
    catchup=False
)

connect = BranchPythonOperator(task_id='connect',
                               python_callable=connect_to_server,
                               provide_context=True,
                               dag=dag)

mount = BashOperator(task_id='mount',
                    bash_command='mount -t cifs -o username=bpasa_chifobserver,password=barbaros //10.103.1.17/share /home/user/zdrive',
                    run_as_user='air',
                    #bash_command='whoami',
                    xcom_push=True,
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

unmount = BashOperator(task_id='unmount',
                    bash_command='umount /home/user/zdrive',
                    run_as_user='air',
                    dag=dag)

finish = DummyOperator(task_id='finish',
                       dag=dag)

connect >> [mount, finish]
mount >> list_source_folder
list_source_folder >> list_dist_folder
list_dist_folder >> get_missing_files
get_missing_files >> [copy, unmount]
copy >> unmount
unmount >> finish
