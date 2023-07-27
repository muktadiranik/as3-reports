import pymysql
from .celery import celery_app
pymysql.install_as_MySQLdb()