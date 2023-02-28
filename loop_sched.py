import requests

from config.my_settings import HEADER
from config.settings import SITE_URL
from apscheduler.schedulers.blocking import BlockingScheduler

header = HEADER

def rank_api():
    try:
        requests.post(SITE_URL+'user/post_rank', headers=header)
    except:
        pass
    try:
        requests.post(SITE_URL+'user/hot_user', headers=header)
    except:
        pass
    try:
        requests.post(SITE_URL+'user/rank', headers=header)
    except:
        pass

def news_crawling():
    requests.post(SITE_URL+'data/get_data', headers=header)

def set_monthly():
    try:
        requests.post(SITE_URL+'user/tag_count', headers=header)
    except: pass   
    
def set_weekly():
    try:
        requests.post(SITE_URL+'data/company_news', headers=header)
    except: pass
bg_scheuler = BlockingScheduler(timezone="Asia/Seoul")

bg_scheuler.add_job(set_monthly, 'cron', day=1)

bg_scheuler.add_job(set_weekly, 'cron', day='*/14')

bg_scheuler.add_job(news_crawling, 'cron', hour=7)
bg_scheuler.add_job(rank_api, 'cron', hour=22)
bg_scheuler.start()