from celery import Celery
import get_meteo

app = Celery('tasks', broker='amqp://guest:guest@rabbitmq:5672/')


@app.task
def download(start_date, end_date, directory, param, levels):
    return get_meteo.get_meteo(start_date, end_date, directory, param, levels)
