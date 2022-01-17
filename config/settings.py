import os
import firebase_admin

from pathlib import Path
from .my_settings import EMAIL, S3
from firebase_admin import credentials

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-llzvhsk6%r+^g_22*iq2p()39s2+*hrw6jcp(pdhozwtt)&_o='

DEBUG = True

ALLOWED_HOSTS = ["*"]

cred_path = os.path.join(BASE_DIR, "serviceAccountKey.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'post_api.apps.PostApiConfig',
    'user_api.apps.UserApiConfig',
    'project_api.apps.ProjectApiConfig',
    'question_api.apps.QuestionApiConfig',
    'tag.apps.TagConfig',
    'fcm.apps.FcmConfig',
    'loop.apps.LoopConfig',
    'search.apps.SearchConfig',
    'chat',
    
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_yasg',

    'storages'
]

REST_FRAMEWORK = {

    # Web Test 때문에 꺼놈
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ],


    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ]

}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASE_ROUTERS = ['config.router.Router']

DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'main',
        'USER': 'LoopUS',
        'PASSWORD': 'rlagudxo',
        'HOST': 'loop-us.crebljnzwq67.ap-northeast-2.rds.amazonaws.com',
        'PORT': '3306',

    },
    'chatting':{
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'chatting',
        'USER': 'LoopUS',
        'PASSWORD': 'rlagudxo',
        'HOST': 'loop-us.crebljnzwq67.ap-northeast-2.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    },
    'log':{
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'log',
        'USER': 'LoopUS',
        'PASSWORD': 'rlagudxo',
        'HOST': 'loop-us.crebljnzwq67.ap-northeast-2.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# EMAIL SET
SITE_ID = 1

EMAIL_BACKEND = EMAIL['EMAIL_BACKEND']
EMAIL_PORT = EMAIL['EMAIL_PORT']
EMAIL_HOST = EMAIL['EMAIL_HOST']
EMAIL_HOST_USER = EMAIL['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = EMAIL['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = EMAIL['EMAIL_USE_TLS']


# AWS s3설정
# AWS_ACCESS_KEY_ID = 'AKIA4XCDN5N2D2USORU5'
# AWS_SECRET_ACCESS_KEY = '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'

AWS_ACCESS_KEY_ID = S3['access_key']
AWS_SECRET_ACCESS_KEY = S3['secret_key']
AWS_REGION = 'ap-northeast-2'
AWS_STORAGE_BUCKET_NAME = 'loopus'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (
    AWS_STORAGE_BUCKET_NAME, AWS_REGION)
AWS_DEFAULT_ACL = None
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024000000  # value in bytes 1GB here
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024000000
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# AUTH_USER_MODEL = 'user_api.UserCustom'