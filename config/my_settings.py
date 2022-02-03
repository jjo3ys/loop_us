
import os 

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