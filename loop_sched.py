import requests

from apscheduler.schedulers.blocking import BlockingScheduler
header = {'Authorization':'Token 9c661c35fb3d6795f39f7c660a414f17a7fd77ec'}

def rank_api():
    try:
        requests.get('http://3.35.253.151:8000/rank/project_group', headers=header)
    except:
        pass
    try:
        requests.get('http://3.35.253.151:8000/rank/set_ranking', headers=header)
    except:
        pass
    try:
        requests.get('http://3.35.253.151:8000/rank/set_profile_group', headers=header)
    except:
        pass
    try:
        requests.get('http://3.35.253.151:8000/rank/user_ranking', headers=header)
    except:
        pass

def news_crawling():
    requests.get('http://3.35.253.151:8000/get_data/news', headers=header)

def set_monthly_tag_count():
    requests.get('http://3.35.253.151:8000/rank/tag_count', headers=header)

def set_group_monthly_trends():
    requests.post('http://3.35.253.151:8000/rank/posting_trends', headers=header)
    

bg_scheuler = BlockingScheduler(timezone="Asia/Seoul")

bg_scheuler.add_job(set_monthly_tag_count, 'cron', day=1)
bg_scheuler.add_job(set_group_monthly_trends, 'cron', day=1)

bg_scheuler.add_job(news_crawling, 'cron', hour=7)
bg_scheuler.add_job(rank_api, 'cron', hour=22)
bg_scheuler.start()