from .base import *
from dotenv import load_dotenv
import os

print("I am running in local env")

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
# take environment variables from .env.
load_dotenv(os.path.join(PROJECT_DIR, ".env/.local"))

SECRET_KEY = "0^43(2+3foirw0f*g!!fesf=aiozu4va@7sg0(m_ouiyr)560x"
# SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
SENDGRID_APIKEY = os.environ.get("SENDGRID_API_KEY")

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

TESTING_LOCAL_APPS = [
    'debug_toolbar'
]

INSTALLED_APPS += TESTING_LOCAL_APPS

DOMAIN = os.environ.get("DOMAIN")
S3_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.environ.get("S3_BUCKET_LOCAL")

INTERNAL_IPS = [
    "127.0.0.1",
]

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'as3_new',
#         'OPTIONS': {
#             'init_command': 'SET innodb_strict_mode=1',
#         },
#         'USER': os.environ.get("DBUSER"),
#         'PASSWORD': os.environ.get("DBPASSWORD"),
#         'HOST': os.environ.get("DBHOST"),
#         'PORT': 3306
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'staticfiles')
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'as3/media')
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'
