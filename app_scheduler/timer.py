from apscheduler.schedulers.background import BackgroundScheduler
from crawling_api.views import *

def start():
    bg_scheuler = BackgroundScheduler(timezone="Asia/Seoul")
    # bg_scheuler.add_job(news_crawling, 'cron', second=30)
    bg_scheuler.add_job(news_crawling, 'cron', hour=7, minute=0, second=0)
    bg_scheuler.start()