from celery import Celery


app = Celery('bot', broker='redis://localhost:6379/3')

# TODO: place celery config
