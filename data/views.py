from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework import status

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from googleapiclient.discovery import build

from config.settings import COUNT_PER_PAGE
from config.my_settings import YOUTUBEKEY, LINUX_CHROME_DRIVER, WINDOW_CHROME_DRIVER

from career.models import Tag
from data.serializers import BrunchSerializer, NewsSerializer, YoutubeSerializer

from user.models import Company_Inform

from .models import *

import platform

# 메인 페이지 뉴스, 영상 데이터 크롤링
class GetData(APIView):
    def __init__(self):
        if platform.system() == "Linux":
            self.path = LINUX_CHROME_DRIVER
        else: self.path = WINDOW_CHROME_DRIVER

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--single-process")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

        self.google_url  = "https://www.google.com/search?tbm=nws&q="
        self.brunch_url  = "https://brunch.co.kr/search"
        self.youtube_url = "https://www.youtube.com/watch?v="

    def post(self, request):
        user = request.user

        if user.id != 5: return Response(status=status.HTTP_403_FORBIDDEN)

        driver  = webdriver.Chrome(self.path, chrome_options=self.chrome_options)
        driver.implicitly_wait(10)
        youtube = build("youtube", "v3", developerKey=YOUTUBEKEY)

        news_last = News.objects.last()
        yt_last   = Youtube.objects.last()
        br_last   = Brunch.objects.last()

        news_obj_list = []
        br_obj_list   = []
        yt_obj_list   = []

        # 인기 태그 top N 개
        pop_tags = Tag.objects.all().order_by("-count")[:5]
        for tag in pop_tags:
            # 구글 뉴스 검색
            driver.get(self.google_url+tag.tag)
            
            a_tags = driver.find_elements_by_tag_name("a")
            
            count = 0
            content_list = []
            
            for a_tag in a_tags:
                if a_tag.get_attribute("jsname") == "YKoRaf":
                    link = a_tag.get_attribute("href")
                    content_list.append(link)
                    count += 1
                if count == 3: break
            
            count = 0
            div_tags = driver.find_elements_by_tag_name("div")
            for div_tag in div_tags:
                if div_tag.get_attribute("classs") == "CEMjEf NUnG9d":
                    publisher = div_tag.find_element_by_tag_name("span").text
                    news_obj_list.append(News(urls=content_list[count], corp=publisher))
                    count += 1
                if count == 3: break

            # 카카오 브런치 검색
            driver.get(self.brunch_url)
            driver.find_element_by_class_name("txt_search").send_keys(tag.tag+Keys.ENTER)
           
            content_list = []

            count = 0
            n     = 1
            while count <=3:
                try:
                    link = driver.find_element_by_xpath(f'//*[@id="resultArticle"]/div/div[1]/div[2]/ul/li[{n}]/a')
                except NoSuchElementException:
                    n += 1
                    continue
                link = link.get_attribute("href")
                content_list.append(link)
                count += 1
            
            for link in content_list:
                driver.get(link)
                
                writer    = driver.find_element_by_xpath("/html/body/div[3]/div[3]/div/div[1]/strong/a").text
                image_url = driver.find_element_by_xpath("/html/body/div[3]/div[3]/div/div[1]/a/img").get_attribute("src")
                
                br_obj_list.append(Brunch(urls=link, writer=writer, profile_url=image_url))

            # 유튜브 검색
            results = youtube.search().list(
                q          = tag.tag,
                order      = "relevance",
                part       = "snippet",
                maxResults = 10
            ).execute()

            count = 0
            for result in results["items"]:
                if result["id"]["kind"] == "youtube#viedo":
                    try:
                        video_id = result["id"]["videoId"]
                    except AttributeError: continue
                    link = self.youtube_url + video_id
                    yt_obj_list.append(Youtube(urls=link))
                    count += 1
                if count == 3: break

        News.objects.bulk_create(news_obj_list)
        Brunch.objects.bulk_create(br_obj_list)
        Youtube.objects.bulk_create(yt_obj_list)

        try:
            News.objects.filter(id__lte=news_last.id).delete()
            Brunch.objects.filter(id__lte=br_last.id).delete()
            Youtube.objects.filter(id__lte=yt_last.id).delete()
        except: pass
        driver.close()

        return Response(status=status.HTTP_200_OK)
    
    def get(self, request):
        results = {}

        news_obj = News.objects.all().order_by("?")
        br_obj   = Brunch.objects.all().order_by("?")
        yt_obj   = Youtube.objects.all().order_by("?")

        results["news"]    = NewsSerializer(news_obj, many=True, read_only=True).data
        results["brunch"]  = BrunchSerializer(br_obj, many=True, read_only=True).data
        results["youtube"] = YoutubeSerializer(yt_obj, many=True, read_only=True).data

        return Response(results, status=status.HTTP_200_OK)
        
# 회사 연관 뉴스
class CompanyNewsData(GetData):
    def post(self, request):
        user = request.user
        if user.id != 5: return Response(status=status.HTTP_403_FORBIDDEN)

        driver = webdriver.Chrome(self.path, chrome_options=self.chrome_options)
        driver.implicitly_wait(10)

        last_news = CompanyNews.objects.last()
        companies = Company_Inform.objects.all()
        news_obj_list = []

        for company in companies:
            count = 0
            content_list = []

            driver.get(self.google_url+"기업"+company.company_name)
            a_tags = driver.find_elements_by_tag_name("a")

            for a_tag in a_tags:
                if a_tag.get_attribute("jsname") == "YKoRaf":
                    link = a_tag.get_attribute("href")
                    content_list.append(link)
                    count += 1
                if count == 5: break
                
                count = 0
                div_tags = driver.find_elements_by_tag_name("div")
                for div_tag in div_tags:
                    if div_tag.get_attribute("classs") == "CEMjEf NUnG9d":
                        publisher = div_tag.find_element_by_tag_name("span").text
                        news_obj_list.append(News(urls=content_list[count], corp=publisher))
                        count += 1
                    if count == 5: break
            
        CompanyNews.objects.bulk_create(news_obj_list)
        if last_news:
            CompanyNews.objects.filter(id__lte=last_news.id).delete()

        return Response(status=status.HTTP_200_OK)
        