# import paramiko
from airflow.models import Variable
import os, shutil
import logging
from pathlib import Path
import ftplib
import pathlib

logger = logging.getLogger("airflow.task")

def connect_to_server(**kwargs):
    pass


def read_source_folder(**kwargs):
    pass


def read_dist_folder(**kwargs):
    pass


def compare_log_files(**kwargs):
    pass


def copy(**kwargs):
    pass
