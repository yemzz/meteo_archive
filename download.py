import json
import datetime
import time
import os
from dateutil.relativedelta import relativedelta
from tasks import download
from tasks import app

def main():
    download_date = datetime.date(2019, 6, 1)
    first_day_next_month = download_date
    final_date = datetime.date(2019, 6, 2)
    print("here")

    with open('meteo_archive_info.json') as f:
        archive_info = json.load(f)

    for param in archive_info.keys():
        while download_date != final_date:
            time.sleep(1)
            date_path = "./archive_files/" + param + "/" + download_date.strftime("%Y-%m")
            if not os.path.exists(date_path):
                os.makedirs(date_path)
            first_day_next_month += relativedelta(months=1)
            task_name = "weather_download_temp"
            handler_task = app.signature(task_name,
                                         args={"start_date": download_date.strftime("%Y%m%d"),
                                                 "end_date": (first_day_next_month - relativedelta(days=1)).strftime("%Y%m%d"),
                                                 "directory": date_path,
                                                 "param": param,
                                                 "levels": archive_info[param]["levels"]
                                                 },
                                         queue="tasks.download")

            handler_task.apply_async()
            # download.delay(download_date.strftime("%Y%m%d"),
            #                (first_day_next_month - relativedelta(days=1)).strftime("%Y%m%d"), date_path, param,
            #                archive_info[param]["levels"])
            download_date = first_day_next_month


if __name__ == "__main__":
    main()
