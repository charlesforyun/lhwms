import logging
import django.utils.log
import logging.handlers
import os
from lhwms.settings import MEDIA_ROOT

log_path = os.path.join(MEDIA_ROOT, "logs")

if not os.path.exists(log_path):
    os.makedirs("logs")

# DJANGO_LOG_LEVEL=DEBUG

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'all.log'),
        # 或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'debug.log'),
        # 或者直接写路径：'c:\logs\all.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    # DEBUG(测试环境) CRITICAL(项目崩溃)  ERROR(抛出异常未被捕获) WARNING(例如403) INFO(系统表现相关)
    'loggers': {
        'print': {
            'handlers': ["file"],
            'level': 'INFO',
            'propagate': False
        },
        'ifacerecognition': {
            'handlers': ['default'],
            'level': 'ERROR',
        },
        # 'django': {
        #   'handlers': ['default'],
        #   'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        # },
        'django.request': {
            'handlers': ['default'],
            'level': 'ERROR',
        },
    },
}