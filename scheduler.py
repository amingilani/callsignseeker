from apscheduler.schedulers.blocking import BlockingScheduler
from callsignchecker import main as callsignchecker

sched = BlockingScheduler()


@sched.scheduled_job("cron", timezone="America/Toronto", hour=7, minute=00)
def scheduled_job():
    callsignchecker()


sched.start()
