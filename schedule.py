import schedule
import time
import os


def job():
    print("Executing job...")
    os.system("python main.py")


schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
