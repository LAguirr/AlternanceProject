from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
import shutil
import os
from ..core.celery_app import celery_app
from ..services.trainer import train_model_task

router = APIRouter(prefix='/datasets', tags=['datasets'])

UPLOAD_DIR = os.getenv('UPLOAD_DIR', '/code/datasets')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post('/upload', response_model=schemas.DatasetOut)
async def upload_dataset(name: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # TODO: obtener user desde auth. Para MVP asumimos user_id=1
    user_id = 1
    filename = f"{user_id}_{file.filename}"
    dest = os.path.join(UPLOAD_DIR, filename)
    with open(dest, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_ds = models.Dataset(user_id=user_id, name=name, filename=filename)
    db.add(db_ds)
    db.commit()
    db.refresh(db_ds)

    return db_ds

@router.get('/{dataset_id}/preview')
def preview_dataset(dataset_id: int, db: Session = Depends(get_db)):
    ds = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(404, 'Dataset not found')
    path = os.path.join(UPLOAD_DIR, ds.filename)
    import pandas as pd
    df = pd.read_csv(path, nrows=100)
    return {'columns': df.columns.tolist(), 'sample_rows': df.head(5).to_dict(orient='records')}

@router.post('/{dataset_id}/train')
def train(dataset_id: int, req: schemas.TrainRequest, db: Session = Depends(get_db)):
    ds = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(404, 'Dataset not found')
    path = os.path.join(UPLOAD_DIR, ds.filename)
    task = train_model_task.delay(path, req.target_column, req.model_type, req.model_name)
    return {'task_id': task.id}