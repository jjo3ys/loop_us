import platform
import time

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from googleapiclient.discovery import build

from .models import News, Brunch, Youtube

from tag.models import Tag, Group
from config.my_settings import YOUTUBEKEY

if platform.system() == 'Linux':
    path = '/home/ubuntu/loopus/chromedriver'
else:
    path = 'chromedriver'

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument("--single-process")
# chrome_options.add_argument("--disable-dev-shm-usage")

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def crawling(request):
    if request.user.id !=5:
        return Response(status=status.HTTP_403_FORBIDDEN)

    driver = webdriver.Chrome(path, chrome_options=chrome_options)
    driver.implicitly_wait(10)
    youtube = build('youtube', 'v3', developerKey=YOUTUBEKEY)

    group_id = Group.objects.all()
    last_news = News.objects.last()
    last_yt = Youtube.objects.last()
    last_br = Brunch.objects.last()
    #Naver
    # url = 'https://search.naver.com/search.naver?where=news&query='
    #Goggle
    url = 'https://www.google.com/search?tbm=nws&q='
    for group in group_id:
        tag_list = Tag.objects.filter(group_id=group.id).order_by('-count')[:5]
        link_dict = {}
        
        for tag in tag_list:
            try:
                news_url = url+tag.tag
                driver.get(news_url)
                news_count = 0
                a_tag = driver.find_elements_by_tag_name('a')
                link_map = []
                for a in a_tag:
                    if a.get_attribute('jsname') == 'YKoRaf':
                        link = a.get_attribute('href')
                        if link not in link_dict:
                            link_map.append(link)
                            link_dict[link] = True
                            news_count += 1
                    if news_count == 3:
                        break
                    
                news_count = 0
                div_tag = driver.find_elements_by_tag_name('div')
                for div in div_tag:
                    if div.get_attribute('class') == 'CEMjEf NUnG9d':
                        txt = div.find_element_by_tag_name('span').text
                        News.objects.create(urls=link_map[news_count], group=group, corp=txt)
                        news_count += 1
                    if news_count == 3:
                        break
                        
            except:pass
            try:
                driver.get('https://brunch.co.kr/search')
                driver.find_element_by_class_name('txt_search').send_keys(tag.tag+Keys.ENTER)
                time.sleep(2)
                count = 0
                results = driver.find_elements_by_class_name('link_post')
                for result in results:
                    link = result.get_attribute('href')
                    driver.get(link)
                    time.sleep(2)
                    writer = driver.find_element_by_xpath('/html/body/div[3]/div[3]/div/div[1]/strong/a').text
                    image_url = driver.find_element_by_xpath('/html/body/div[3]/div[3]/div/div[1]/a/img').get_attribute('src')
                    driver.back()
                    count +=1
                    Brunch.objects.create(urls=link, group=group, writer=writer, profile_url=image_url)
                    
                    if count == 3:
                        break   
            except:pass
            try:
                results = youtube.search().list(q=tag.tag, order='relevance', part='snippet', maxResults=10).execute()
                count = 0
                for result in results['items']:
                    
                    if result['id']['kind'] == 'youtube#video':
                        try:
                            video_id = result['id']['videoId']
                        except AttributeError:
                            continue
                        link = 'https://www.youtube.com/watch?v=' + video_id
                        Youtube.objects.create(urls=link, group=group)
                        count += 1
                    if count == 3:
                        break
            except:
                pass
    try:
        News.objects.filter(id__lte=last_news.id).delete()
        Youtube.objects.filter(id__lte=last_yt.id).delete()
        Brunch.objects.filter(id__lte=last_br.id).delete()
    except AttributeError:
        pass
    driver.close()
    return Response(status=status.HTTP_200_OK)