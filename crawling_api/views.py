import platform

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from selenium import webdriver
from googleapiclient.discovery import build

from .models import News, Insta, Youtube

from tag.models import Tag, Group
from config.my_settings import YOUTUBEKEY

if platform.system() == 'Linux':
    path = '/home/ubuntu/loopus/chromedriver'
else:
    path = 'chromedriver'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--single-process")
chrome_options.add_argument("--disable-dev-shm-usage")

def feed_crawling(type):
    if type == 'insta':
        pass

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def crawling(request):
    if request.user.id !=5:
        return Response(status=status.HTTP_403_FORBIDDEN)

    driver = webdriver.Chrome(path, chrome_options=chrome_options)
    youtube = build('youtube', 'v3', developerKey=YOUTUBEKEY)

    group_id = Group.objects.all()
    last_news = News.objects.last()
    last_yt = Youtube.objects.last()
    #Naver
    # url = 'https://search.naver.com/search.naver?where=news&query='
    #Goggle
    url = 'https://www.google.com/search?tbm=nws&q='
    for group in group_id:
        tag_list = Tag.objects.filter(group_id=group.id).order_by('-count')[:5]
        link_dict = {}
        for tag in tag_list:
            news_url = url+tag.tag
            driver.get(news_url)
            news_count = 0
            a_tag = driver.find_elements_by_tag_name('a')
            for a in a_tag:
                if a.get_attribute('jsname') == 'YKoRaf':
                    link = a.get_attribute('href')
                    if link not in link_dict:
                       # News.objects.create(urls=link, group=group)
                        link_dict[link] = True
                        news_count += 1
                if news_count == 3:
                    break

            results = youtube.search().list(q=tag.tag, order='rating', part='snippet', maxResults=10).execute()
            for result in results['items']:
                if result['id']['kind'] == 'youtube#video':
                    video_id = result['id']['videoID']
                    link = 'https://www.youtube.com/watch?v=' + video_id
                    Youtube.objects.create(urls=link, group=group)
    try:
        News.objects.filter(id__lte=last_news.id).delete()
        Youtube.objects.filter(id__lte=last_yt.id).delete()
    except AttributeError:
        pass
    driver.close()
    return Response(status=status.HTTP_200_OK)
