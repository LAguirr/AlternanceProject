import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, crud, schemas
from .tasks import train_task
from .api import datasets


# Crear tablas (MVP: create_all)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="IA para PYMES - API")
app.include_router(datasets.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
def root():
    return {'ok': True}


@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # En este MVP asumimos user_id = 1
    user_id = 1
    datasets_dir = "datasets"
    os.makedirs(datasets_dir, exist_ok=True)
    file_path = os.path.join(datasets_dir, file.filename)
    with open(file_path, "wb") as f:
        contents = await file.read()
        f.write(contents)

    ds = crud.create_dataset(db, user_id=user_id, filename=file.filename, path=file_path)
    return {"dataset_id": ds.id, "filename": ds.filename}

@app.get("/datasets/{dataset_id}/preview")
def preview_dataset(dataset_id: int, db: Session = Depends(get_db)):
    ds = crud.get_dataset(db, dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    import pandas as pd
    df = pd.read_csv(ds.path, nrows=10)
    return JSONResponse(content={"preview": df.to_dict(orient="records")})

@app.post("/models/train")
def train_model(dataset_id: int, target_col: str, db: Session = Depends(get_db)):
    user_id = 1  # MVP: user hardcoded
    ds = crud.get_dataset(db, dataset_id)
    if not ds:
        raise HTTPException(404, "Dataset not found")

    # Launch celery task
    task = train_task.delay(user_id, dataset_id, target_col, "linear_regression")
    return {"task_id": task.id, "status": "started"}

@app.get("/models/{model_id}")
def get_model(model_id: int, db: Session = Depends(get_db)):
    m = crud.get_model(db, model_id)
    if not m:
        raise HTTPException(404, "Model not found")
    return m
