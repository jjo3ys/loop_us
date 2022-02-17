from django.db import models
from django.conf import settings
# Create your models here.

class Portfolio(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    introduction = models.TextField(null=True) # 나는 이런사람입니다  ex) 자기소개 한문장 
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Portfolio'
    
class Element(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, related_name='element', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(null=True, upload_to='element/image/%Y%m%d/')
    title = models.TextField(null=True)
    contents = models.TextField(null=True)

    class Meta:
        db_table = 'Element'
