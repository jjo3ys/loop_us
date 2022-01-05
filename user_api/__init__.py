from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
def job():
    print('외않되?')

sched = BackgroundScheduler(timezone=settings.TIME_ZONE)
sched.start()

sched.add_job(job, 'cron', minute='00', hour='20', day_of_week='fri')