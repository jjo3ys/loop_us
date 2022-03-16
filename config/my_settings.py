
import os 

DJANGO_KEY = 'django-insecure-llzvhsk6%r+^g_22*iq2p()39s2+*hrw6jcp(pdhozwtt)&_o='

EMAIL = {
'EMAIL_BACKEND' : 'django.core.mail.backends.smtp.EmailBackend',
'EMAIL_USE_TLS' : True,
'EMAIL_PORT' : 587,
'EMAIL_HOST' : 'smtp.gmail.com',   
'EMAIL_HOST_USER' : 'loopus@loopus.co.kr',                    
'EMAIL_HOST_PASSWORD' : 'yzqdfakjynpbozle',
# 'REDIRECT_PAGE' : 'http://10.58.5.40:3000/signin'
}
# YS's S3 config
# S3 = {
#     'access_key':'AKIA4XCDN5N2IUMDHTQG',
#     'secret_key':'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'
# }
# MyLoop's S3 config
S3 = {
    'access_key':'AKIAUJMINUHA626SK34A',
    'secret_key':'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'
}

DB_SETTING = {
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