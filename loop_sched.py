import requests

from apscheduler.schedulers.blocking import BlockingScheduler
header = {'Authorization':'Token 9c661c35fb3d6795f39f7c660a414f17a7fd77ec'}

def posting_ranking():
    requests.get('http://127.0.0.1:8000/rank/set_ranking', headers=header)

def news_crawling():
    requests.get('http://127.0.0.1:8000/get_data/news', headers=header)

def set_monthly_tag_count():
    requests.get('http://127.0.0.1:8000/rank/tag_count', headers=header)

def set_group_monthly_trends():
    requests.post('http://127.0.0.1:8000/rank/posting_trends', headers=header)

def set_profile_group():
    requests.get('http://127.0.0.1:8000/rank/set_profile_group', headers=header)

bg_scheuler = BlockingScheduler(timezone="Asia/Seoul")

bg_scheuler.add_job(set_monthly_tag_count, 'cron', day=1)
bg_scheuler.add_job(set_group_monthly_trends, 'cron', day=1)

bg_scheuler.add_job(news_crawling, 'cron', hour=7)
bg_scheuler.add_job(posting_ranking, 'cron', hour=22)
bg_scheuler.add_job(set_profile_group, 'cron', hour=22)

bg_scheuler.start()