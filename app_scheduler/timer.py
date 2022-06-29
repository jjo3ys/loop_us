from apscheduler.schedulers.background import BackgroundScheduler
from crawling_api.views import *
from rank_api.views import *

def start():
    bg_scheuler = BackgroundScheduler(timezone="Asia/Seoul")
    # bg_scheuler.add_job(news_crawling, 'cron', second=30)
    bg_scheuler.add_job(news_crawling, 'cron', hour=7)
    bg_scheuler.add_job(set_monthly_tag_count, 'cron', day=1)
    # bg_scheuler.add_job(posting_ranking, 'cron', hour=22)
    # bg_scheuler.add_job(set_profile_group, 'cron', hour=22)
    bg_scheuler.start()