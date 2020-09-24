from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from core.tension import scan, read_data, move
from core.utils import files_func
from datetime import datetime
 

args = {
    'owner': 'Airflow',
    'start_date': datetime.now(),
    'provide_context': True,
}

dag = DAG(
    dag_id='TensionImport',
    default_args=args,
    schedule_interval='* * * * *',
    tags=['seislog']
)

scan_folder = PythonOperator(task_id='scan_folder',
                             python_callable=scan,
                             provide_context=True,
                             dag=dag)

if_files_exists = BranchPythonOperator(task_id='if_files_exists',
                                       provide_context=True,
                                       python_callable=files_func,
                                       dag=dag)

read_import = PythonOperator(task_id='read_import',
                             python_callable=read_data,
                             provide_context=True,
                             dag=dag)

move_files = PythonOperator(task_id='move',
                            python_callable=move,
                            provide_context=True,
                            dag=dag)

finish = DummyOperator(task_id='finish',
                       dag=dag)

scan_folder >> if_files_exists
if_files_exists >> [read_import, finish]
read_import >> move_files
move_files >> finish
