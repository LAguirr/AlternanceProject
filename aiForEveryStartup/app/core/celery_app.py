from celery import Celery
import os

broker = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery_app = Celery('app', broker=broker, backend=backend)
celery_app.conf.task_routes = {
    'app.services.trainer.train_model_task': {'queue': 'training'}
}