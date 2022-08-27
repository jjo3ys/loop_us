from django.db import models
from django.conf import settings

from user_api.models import Company
from tag.models import Group

# Create your models here.

class Contact(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name = 'scout_company')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "Contact"