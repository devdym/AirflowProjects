from seislogAPI.nav import read_wingAngle
from seislogAPI.folderscaner import scan_folder, logFiles_toMySql
import os, shutil
import logging
from pathlib import Path
from core.utils import read_db, check_project_id, save_project_name_toMySql, check_log_id, save_log_toMySql
from sqlalchemy import create_engine

logger = logging.getLogger("airflow.task")
basepath = Path('/home/user/data_repository/projects/')


def scan(**kwargs):
    files = scan_folder(basepath)
    # filter ballasting logs
    files = dict(filter(lambda elem: "ballasting" in elem[0], files.items()))
    kwargs['ti'].xcom_push(key='import_files', value=files)


def read_data(**kwargs):
    files_list = []
    projectid = None
    importlog_id = None

    # make list of files from folder
    data = kwargs['ti'].xcom_pull(key='import_files', task_ids='scan_folder')

    # for every file
    for k, l in data.items():
        files_list.append(l['file_path'])
        log_path = l['file_path']
        logger.info('files: {}'.format(l['file_path']))

        # get Project name
        projectname = l["project_name"]
        # get Vessel name
        vesselname = l["vessel_name"]

        logger.info('project name: {}, vessel name: {}'.format(projectname, vesselname))

        # search Project_name + vessel_name in Project table
        projectid = check_project_id(projectname, vesselname)
        if projectid is not None:
            # get id
            logger.info('project id {} already exists'.format(projectid))
        else:
            logger.info('project doesn`t exist')
            # add into Project table
            save_project_name_toMySql(projectname, vesselname)
            projectid = check_project_id(projectname, vesselname)
            # get id
            logger.info('project id {} already exists'.format(projectid))
        # search importlog+project_name+vessel_name in importLog+Project tables
        importlog_id = check_log_id(log_path, projectid)
        if importlog_id is not None:
            logger.info('importLog id {}'.format(importlog_id))
        else:
            logger.info('importLog file dosn`t exist')
            # import file into ballasting table
            b = read_wingAngle(log_path)
            wingAngle_toMySql(b, projectid)
            logger.info('IMPORTED')
            # add into importLog
            save_log_toMySql(log_path, projectid)
            logger.info('LOG is UPDATED')


def move(**kwargs):
    task_instance = kwargs['ti']
    data = task_instance.xcom_pull(key='import_files', task_ids='scan_folder')
    for s in data:
        d = os.path.dirname(os.path.abspath(s))
        d = str(s).replace('projects', 'archive')
        shutil.move(s, d)


def wingAngle_toMySql(data, id):
    data['project_id'] = id
    # create sqlalchemy engine
    engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
						   .format(user="usersql",
								   pw="usersql",
								   db="aurora_light"))
    data.to_sql('ballasting', con=engine, if_exists='append', chunksize=1000, index=False)
    # print("**inserted**")
