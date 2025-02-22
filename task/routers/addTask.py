from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from .. import models, schemas, database
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add-task/")
def add_task(request: schemas.TaskCreate, db: Session = Depends(get_db)):
    file = db.query(models.FileUpload).filter(models.FileUpload.resource_id == request.resource_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found. Please provide a valid resource_id.")

    if not os.path.exists(file.resource_location):
        raise HTTPException(status_code=404, detail="File not found at the specified location.")

    valid_models = ["logistic_regression", "decision_tree", "random_forest", "gradient_boosting", "svm", "knn", "xgboost"]
    if request.model_type not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model type: {request.model_type}. Supported models: {valid_models}")

    new_task = models.Task(
        task_id=str(uuid4()),
        resource_id=request.resource_id,
        model_type=request.model_type,
        task_name=str(file.resource_name),
        task_description="Task linked to file",
        task_status="Pending",
        priority="Normal",
        created_on=datetime.utcnow(),
        updated_on=datetime.utcnow(),
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    ml_server_url = "http://127.0.0.1:8001/ml-model/"
    try:
        with open(file.resource_location, "rb") as f:
            response = requests.post(ml_server_url, files={"file": f}, data={"model_type": request.model_type})

        if response.status_code == 200:
            result = response.json()
            new_task.task_status = "Completed"
            new_task.accuracy = result.get("accuracy")
            new_task.f1_score = result.get("f1_score")
            new_task.recall = result.get("recall")
            new_task.precision = result.get("precision")
        else:
            new_task.task_status = "Failed"
            raise HTTPException(status_code=500, detail="Error in ML server: " + response.text)
    except Exception as e:
        new_task.task_status = "Failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error during file processing: {str(e)}")

    db.commit()

    return {
        "message": "Task added and processed successfully.",
        "task_id": new_task.task_id,
        "accuracy": new_task.accuracy,
        "f1_score": new_task.f1_score,
        "recall": new_task.recall,
        "precision": new_task.precision,
    }
