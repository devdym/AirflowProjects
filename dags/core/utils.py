import logging
from sqlalchemy import create_engine
import pandas as pd

logger = logging.getLogger("airflow.task")


def files_func(**kwargs):
    ti = kwargs['ti']
    xcom_value = ti.xcom_pull(key='import_files', task_ids='scan_folder')
    logger.info('There are {} files. Good to continue pipeline'.format(len(xcom_value)))
    if len(xcom_value) > 0:
        return 'read_import'
    else:
        return 'finish'


def read_db(log_type):
    res = []
    engine = create_engine("mysql+pymysql://{user}:{pw}@10.103.1.30/{db}"
                           .format(user="usersql",
                                   pw="usersql",
                                   db="aurora_light"))

    result = engine.execute('SELECT file FROM importLog WHERE file like ":lt"', lt=log_type)
    for r in result:
        logger.info(r[0])
        res.append(r[0])
    return res

def check_project_id(project, vessel):
    res = None
    engine = create_engine("mysql://{user}:{pw}@10.103.1.30/{db}"
                           .format(user="usersql",
                                   pw="usersql",
                                   db="aurora_light"))

    result = engine.execute('SELECT id FROM projects WHERE projectName = %s and vessel = %s', (project, vessel))
    for r in result:

        res = r[0]
    return res

def save_log_toMySql(lineName, id):
	# create sqlalchemy engine
	engine = create_engine("mysql://{user}:{pw}@localhost/{db}"
						   .format(user="usersql",
							pw="usersql",
							db="aurora_light"))
	engine.execute('INSERT INTO importLog (file, projects_id) VALUES (%s, %s)', (lineName, id))

def save_project_name_toMySql(project, vessel):
	# create sqlalchemy engine
	engine = create_engine("mysql://{user}:{pw}@localhost/{db}"
						   .format(user="usersql",
							pw="usersql",
							db="aurora_light"))
	engine.execute('INSERT INTO projects(projectName, vessel) VALUES (%s, %s)', (project, vessel))

def check_log_id(file_path, project_id):
    res = None
    engine = create_engine("mysql://{user}:{pw}@10.103.1.30/{db}"
                           .format(user="usersql",
                                   pw="usersql",
                                   db="aurora_light"))

    result = engine.execute('SELECT id FROM importLog WHERE file like %s and projects_id = %s', (file_path, project_id))
    for r in result:

        res = r[0]
    return res
