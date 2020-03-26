import os
from celery import Celery
import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


app = Celery('tasks', backend='rpc://',include=['tasks'])
app.config_from_object(settings)
app.conf.update(
	enable_utc = True,
	timezone = 'Asia/Almaty')

# #app.conf.CELERY_TIMEZONE = 'Asia/Almaty'
# if __name__ == '__main__':
# 	app.start()
