from sqlalchemy.orm import Session
from . import models, schemas

def create_dataset(db: Session, user_id: int, filename: str, path: str):
    ds = models.Dataset(user_id=user_id, filename=filename, path=path)
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds

def create_model_entry(db: Session, user_id: int, dataset_id: int, name: str, model_path: str, metrics: dict):
    m = models.Model(user_id=user_id, dataset_id=dataset_id, name=name, model_path=model_path, metrics=metrics)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def get_dataset(db: Session, dataset_id: int):
    return db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()

def get_model(db: Session, model_id: int):
    return db.query(models.Model).filter(models.Model.id == model_id).first()
