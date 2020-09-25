# import paramiko
from airflow.models import Variable
import os, shutil
import logging
from pathlib import Path
import ftplib
import pathlib

logger = logging.getLogger("airflow.task")

def connect_to_server(**kwargs):
    server = Variable.get("DigiCourseIP")
    response = os.system("ping -c 1 " + server)

    if response == 0:
        logger.info('DigiCourse host is up! - CONTINUE')
        return 'mount'
    else:
        logger.info('DigiCourse host is down! - STOP')
        return 'finish'


def read_source_folder(**kwargs):
    source = Variable.get("DigiCourseSourceFolder")
    dist = []
    for child in pathlib.Path(source).iterdir():
        if child.is_file():
            dist.append(os.path.split(child)[-1:][0])
    logger.info(dist)


def read_dist_folder(**kwargs):
    pass


def compare_log_files(**kwargs):
    if True:
        return 'copy_files'
    else:
        return 'finish'


def copy(**kwargs):
    pass
