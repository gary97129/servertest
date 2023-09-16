from .settings import *
DEBUG = False
DATABASES = {
'default': {
       'ENGINE': 'django.db.backends.mysql',
        'NAME':'my_db',
        'USER':'root',
        'PASSWORD':'1234567890',
        'HOST':'localhost',
        'POST':'3306',
         'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# celery配置
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'