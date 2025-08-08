import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery("tasks", broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery_app.conf.task_routes = {"app.tasks.train_task": {"queue": "training"}}

# Import here to avoid circular imports at top-level
from .database import SessionLocal
from .crud import create_model_entry, get_dataset
from .services.train import train_linear_regression

@celery_app.task(bind=True)
def train_task(self, user_id: int, dataset_id: int, target_col: str, model_name: str = "linear_regression"):
    db = SessionLocal()
    try:
        ds = get_dataset(db, dataset_id)
        if not ds:
            return {"error": "dataset not found"}

        csv_path = ds.path  # ruta local a datasets/...
        model_path = f"models_storage/user_{user_id}_{dataset_id}_{model_name}.joblib"
        metrics = train_linear_regression(csv_path, target_col, model_path)

        model_entry = create_model_entry(db, user_id=user_id, dataset_id=dataset_id, name=model_name, model_path=model_path, metrics=metrics)
        return {"model_id": model_entry.id, "metrics": metrics}
    except Exception as e:
        raise self.retry(exc=e, countdown=10, max_retries=3)
    finally:
        db.close()
