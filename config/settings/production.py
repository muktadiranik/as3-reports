
from .base import *
from dotenv import load_dotenv
import os

print("I am in production ver settings")

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(PROJECT_DIR, ".env/.production"))  # take environment variables from .env.

DEBUG = False
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
SENDGRID_APIKEY = os.environ.get("SENDGRID_API_KEY")

ALLOWED_HOSTS = [
    "reports.as3international.com"
]

CACHE_MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',     # cache NEW
    # 'django.middleware.cache.FetchFromCacheMiddleware',  # cache NEW
]

DOMAIN = os.environ.get("DOMAIN")
S3_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.environ.get("S3_BUCKET_STUDENT_REPORT")

MIDDLEWARE += CACHE_MIDDLEWARE

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("DBNAME"),
        'OPTIONS': {
            'init_command': 'SET innodb_strict_mode=1',
        },
        'USER': os.environ.get("DBUSER"),
        'PASSWORD': os.environ.get("DBPASSWORD"),
        'HOST': os.environ.get("DBHOST"),
        'PORT': 3306
    }
}

STATIC_ROOT =  "/home/ubuntu/as3/static_cdn"
MEDIA_ROOT = "/home/ubuntu/as3/media_cdn"
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

# SESSION_COOKIE_SECURE = False
# CSRF_COOKIE_SECURE = False
# SECURE_SSL_REDIRECT = False
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

# The age of session cookies, in seconds.
SESSION_COOKIE_AGE = 2*60*60 # 2 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# browsers may ensure that the cookie is only sent under an HTTPS connection.
SESSION_COOKIE_SECURE = True


# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'as3_report.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'MYAPP': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}
