from apscheduler.schedulers.blocking import BlockingScheduler
from callsignchecker import main as callsignchecker

sched = BlockingScheduler()


@sched.scheduled_job("cron", timezone="America/Toronto", hour=10)
def scheduled_job():
    """This job is run every dat at  at 10 am."""
    callsignchecker()


sched.start()
