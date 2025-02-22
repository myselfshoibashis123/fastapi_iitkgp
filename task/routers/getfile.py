from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from . import upload
import os
import uuid
from uuid import uuid4
from pathlib import Path
import json

router = APIRouter()
BASE_DIR = upload.BASE_DIR

@router.get("/files/{unique_id}")
async def get_file(unique_id: str):
    storage_path = BASE_DIR/unique_id
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    files = list(storage_path.iterdir())
    file_info = [
        {"file_name": file.name, "file_path": str(file)}
        for file in files
        if file.is_file() and file.name != "metadata.json"
    ]
    metadata_path = BASE_DIR/str(unique_id)/"metadata.json"
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Metadata not found")
    with open(metadata_path, "r") as meta:
        metadata = json.load(meta)

    return JSONResponse(
        content={
            "metadata": metadata
        },
        status_code=200
    )
