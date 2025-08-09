from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DatasetCreate(BaseModel):
    name: str

class DatasetOut(BaseModel):
    id: int
    name: str
    filename: str
    created_at: datetime

    class Config:
        orm_mode = True

class TrainRequest(BaseModel):
    dataset_id: int
    target_column: str
    model_type: str = 'linear'  # linear, xgboost, simple_nn
    model_name: Optional[str] = None