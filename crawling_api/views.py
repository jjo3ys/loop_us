import platform

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException as NE

from .models import News, Insta, Youtube

from tag.models import Tag, Group

if platform.system() == 'Linux':
    path = '/home/ubuntu/loopus/chromedriver'
else:
    path = 'C:\\project\\loop\\chromedriver'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--single-process")
chrome_options.add_argument("--disable-dev-shm-usage")

def feed_crawling(type):
    if type == 'insta':
        pass

@api_view(['GET', ])
def news_crawling(request):
    driver = webdriver.Chrome(path, chrome_options=chrome_options)
    url = 'https://search.naver.com/search.naver?where=news&query='

    group_id = Group.objects.all()
    last = News.objects.all().last()

    for group in group_id:
        tag_list = Tag.objects.filter(group_id=group.id).order_by('-count')[:5]
        for tag in tag_list:
            news_url = url+tag.tag
            driver.get(news_url)
            news_count = 0
            for i in range(1, 4):            
                try:
                    link = driver.find_element_by_css_selector('#sp_nws{} > div.news_wrap.api_ani_send > div > a'.format(i+news_count)).get_attribute('href')
                    sub_news_list = driver.find_elements_by_css_selector('#sp_nws{} > div.news_cluster > ul > li'.format(i+news_count))
                    news_count += len(sub_news_list)
                except:
                    try:                        
                        link = driver.find_element_by_css_selector('#sp_nws{} > div > div > a'.format(i+news_count)).get_attribute('href')
                    except:
                        pass
                
                try:
                    News.objects.create(urls=link, group=group)
                except:
                    continue
    News.objects.filter(id__lte=last.id).delete()
    driver.close()
    return Response(status=status.HTTP_200_OK)