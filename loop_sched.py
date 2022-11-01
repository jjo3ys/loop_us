import requests

from apscheduler.schedulers.blocking import BlockingScheduler
header = {'Authorization':'Token 9c661c35fb3d6795f39f7c660a414f17a7fd77ec'}

def rank_api():
    try:
        requests.post('http://3.35.253.151:8000/rank/posting_ranking', headers=header)
    except:
        pass
    try:
        requests.post('http://3.35.253.151:8000/rank/hot_user', headers=header)
    except:
        pass
    try:
        requests.get('http://3.35.253.151:8000/rank/project_group', headers=header)
    except:
        pass
    # try:
    #     requests.get('http://3.35.253.151:8000/rank/profile_group', headers=header)
    # except:
    #     pass
    try:
        requests.get('http://3.35.253.151:8000/rank/user_ranking', headers=header)
    except:
        pass

def news_crawling():
    requests.get('http://3.35.253.151:8000/get_data/crawling', headers=header)

def set_monthly():
    try:
        requests.get('http://3.35.253.151:8000/rank/tag_count', headers=header)
    except: pass
    try:
        requests.post('http://3.35.253.151:8000/rank/posting_trends', headers=header)
    except: pass    
    
def set_weekly():
    try:
        requests.get('http://3.35.253.151:8000/get_data/company_news', headers=header)
    except: pass
bg_scheuler = BlockingScheduler(timezone="Asia/Seoul")

bg_scheuler.add_job(set_monthly, 'cron', day=1)

bg_scheuler.add_job(set_weekly, 'cron', day='*/14')

bg_scheuler.add_job(news_crawling, 'cron', hour=7)
bg_scheuler.add_job(rank_api, 'cron', hour=22)
bg_scheuler.start()