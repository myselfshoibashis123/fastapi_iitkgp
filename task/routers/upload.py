from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import models, database

from fastapi.responses import JSONResponse
import os
import uuid
from uuid import uuid4
from pathlib import Path
import json
import time


router = APIRouter()
BASE_DIR = Path("./uploaded_files")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/upload/')
async def upload_file(file : UploadFile = File(...), description : str = Form(...), db : Session = Depends(get_db)):
    
    start = time.time()

    unique_id = str(uuid4())
    storage_path = BASE_DIR/unique_id
    storage_path.mkdir(parents=True, exist_ok=True)
    file_path = storage_path/file.filename

    new_file = models.FileUpload(resource_id = str(unique_id), resource_name = str(file.filename), resource_description = description, resource_location = str(file_path))
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    #Save the file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    end = time.time()
    # print(f"Execution time: {end-start}")

    metadata = {
        "file_name": file.filename,
        "description": description,
        "file_path": str(file_path),
    }
    
    metadata_file = storage_path/"metadata.json"
    with open(metadata_file, "w") as meta:
        json.dump(metadata, meta)
    
    #Return response
    return JSONResponse(
        content={
            "message": "File uploaded successfully!",
            "file_name": file.filename,
            "file_path": str(file_path),
            "description": description,
        },
        status_code=200,
    )
