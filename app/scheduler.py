import schedule
import time
from app.monitor import monitor_hosts

def run_scheduler():
    schedule.every(10).seconds.do(monitor_hosts)  # sebelumnya mungkin 60 detik
    while True:
        schedule.run_pending()
        time.sleep(1)
