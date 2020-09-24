from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import psycopg2
import sqlalchemy
import datetime
from airflow.utils.dates import days_ago

args = {
    'owner': 'Airflow',
    'start_date': days_ago(2),
}

dag = DAG(dag_id='timeDAG', default_args=args, schedule_interval='* * * * *')

# Define the ETL function
def etl():
    currDate = datetime.datetime.now()
    inf = pd.DataFrame(columns=['time_', 'message'])
    inf = inf.append({'time_': currDate, 'message': 'now'}, ignore_index=True)
    print(inf.head())

    engine = sqlalchemy.create_engine("postgresql://postgres:100pda@localhost/Aurora")
    con = engine.connect()
    table_name = 'debug'
    inf.to_sql(table_name, con, if_exists='append', index=False)
    con.close()

# Define the ETL task using PythonOperator
etl_task = PythonOperator(task_id='timedag',
                          python_callable=etl,
                          dag=dag)
