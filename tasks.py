from celery import Celery
import get_meteo
import os
import settings
from celery import shared_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('tasks', backend='rpc://')
app.config_from_object(settings)
app.conf.update(
    enable_utc=True,
    timezone='Asia/Almaty')


@shared_task(bind=True, ignore_result=True, name='weather_download_temp',
             queue='tasks.download')
def download(self, start_date, end_date, directory, param):
    get_meteo.get_meteo(start_date, end_date, directory, param)
