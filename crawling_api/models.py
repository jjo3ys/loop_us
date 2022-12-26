from django.db import models
from tag.models import Group
from user_api.models import Company_Inform, Department, School
from project_api.models import Project
class News(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_news', on_delete=models.DO_NOTHING)
    corp = models.TextField(default=None, null=True)

    class Meta:
        db_table = "News"

class Brunch(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_brunch', on_delete=models.DO_NOTHING)
    writer = models.CharField(max_length=20)
    profile_url = models.TextField(null=True)

    class Meta:
        db_table = "Brunch"

class Youtube(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_youtube', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "Youtube"
        
class CompanyNews(models.Model):
    urls = models.TextField()
    company = models.ForeignKey(Company_Inform, related_name='company_news', on_delete=models.CASCADE)
    corp = models.TextField(default=None, null=True)
    
    class Meta:
        db_table = "Comapny_News"

class OutsideInform(models.Model):
    type = models.SmallIntegerField(null=True, default=0)
    group = models.SmallIntegerField()
    content = models.TextField()
    image = models.TextField()
    title = models.CharField(max_length=50)
    organizer = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()
    view_count = models.PositiveIntegerField(default=0)
    tagged_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "OutsideInform"
        
class SchoolNews(models.Model):
    school = models.ForeignKey(School, related_name='school_news', on_delete=models.DO_NOTHING)
    cat = models.CharField(max_length=20)
    title = models.CharField(max_length=50)
    image = models.TextField()
    url = models.TextField()
    content = models.TextField()
    upload_date = models.DateField()
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = "School_News"
        
class SchoolProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='school_project')
    school_news = models.ForeignKey(SchoolNews, on_delete=models.DO_NOTHING, related_name='school_news')
    
    class Meta:
        db_table = "SchoolProject"

class ClassInform(models.Model):   
    school = models.ForeignKey(School, related_name='class_school', on_delete=models.CASCADE)
    class_type = models.CharField(max_length=150)
    class_name = models.CharField(max_length=150)
    
    class Meta:
        db_table = "ClassInform"
              
class ClassProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='class_project')
    class_inform = models.ForeignKey(ClassInform, on_delete=models.DO_NOTHING, related_name='class_inform')
    
    class Meta:
        db_table = 'ClassProject'

class OutProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='outside_project')
    out_inform = models.ForeignKey(OutsideInform, on_delete=models.DO_NOTHING, related_name='outside_inform')
    
    class Meta:
        db_table = 'OutProject'

# Create your models here.
outproject_map = {
    0:{
        '기획/아이디어':0,
        '정책/제안/공로':1,
        '광고/홍보/마케팅':2,
        '논문/논술/학술/리포트':3,
        '네이밍/슬로건/카피라이팅':4,
        '영상/UCC/영화':5,
        '사진/이미지/SNS콘텐츠':6,
        '수기/후기/감상문/글짓기':7,
        '문학/시나리오/스토리':8,
        '캐릭터/웹툰/만화':9,
        '디자인/패션/제품':10,
        '아트/미술/공예':11,
        '음악/무용/공연/연기':12,
        'IT/웹/모바일/게임':13,
        '과학/공학/기술':14,
        '건축/건설/인테리어':15,
        '취업/창업':16,
        '모의영연/발표/토론':17,
        '이벤트/기타':18
    },
    1:{
        '마케터':0,
        '서포터즈':1,
        '리포터/객원기자':2,
        '모니터':3,
        '체험단':4,
        '재능기부':5,
        '봉사활동':6,
        '캠프':7,
        '취업/창업':8,
        '교육/강연/세미나':9,
        '전시/페스티벌':10,
        '해외탐방':11,
        '기타':12
    }
}