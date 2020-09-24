# import paramiko
from airflow.models import Variable
import os, shutil
import logging
from pathlib import Path
import ftplib
import pathlib

logger = logging.getLogger("airflow.task")

def connect_to_server(**kwargs):
    # server = Variable.get("GLserver")
    # try:
    #     ssh_client = paramiko.SSHClient()
    #     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     ssh_client.connect(hostname=server, username="display", password='')
    #     return 'read_source'
    # except:
    #     return 'finish'

    try:
        source = Variable.get("GLsource_path")
        server = Variable.get("GLserver")
        ftp = ftplib.FTP(server)
        ftp.login("display", "")
        ftp.quit()
        return 'read_source'
    except:
        return 'finish'


def read_source_folder(**kwargs):
    source = Variable.get("GLsource_path")
    server = Variable.get("GLserver")

    ftp = ftplib.FTP(server)
    ftp.login("display", "")

    files = []
    s_files = []

    ftp.cwd(source)
    ftp.dir(files.append)
    ftp.quit()

    for f in files:
        logger.info(f.split(' ')[-1])
        s_files.append(f.split(' ')[-1])

    kwargs['ti'].xcom_push(key='source_files', value=s_files)


def read_dist_folder(**kwargs):
    destanation = Variable.get("GLdestanation_path")

    files = []
    for child in pathlib.Path(destanation).iterdir():
        if child.is_file():
            files.append(os.path.split(child)[-1:][0])

    logger.info(files)
    kwargs['ti'].xcom_push(key='dist_files', value=files)


def compare_log_files(**kwargs):
    source_files = kwargs['ti'].xcom_pull(key='source_files', task_ids='read_source')
    dist_files = kwargs['ti'].xcom_pull(key='dist_files', task_ids='read_dist')

    files_to_copy = [x for x in source_files if x not in dist_files]
    logger.info(files_to_copy)

    kwargs['ti'].xcom_push(key='files_list', value=files_to_copy)

    if len(files_to_copy)>0:
        return 'copy_files'
    else:
        return 'finish'


def copy(**kwargs):
    # pass
    files = kwargs['ti'].xcom_pull(key='files_list', task_ids='get_missing_files')
    destanation = Variable.get("GLdestanation_path")
    server = Variable.get("GLserver")
    source = Variable.get("GLsource_path")

    ssh_client =paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=server, username="display", password='')
    ftp_client=ssh_client.open_sftp()
    for f in files:
        ftp_client.get(source + f, destanation + f)
    ftp_client.close()
