from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job("cron", timezone="America/Toronto", hour=10)
def scheduled_job():
    print("This job is run every dat at  at 10 am.")


sched.start()
