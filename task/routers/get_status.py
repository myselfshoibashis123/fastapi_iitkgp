from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from . import upload
import os
import uuid
from uuid import uuid4
from pathlib import Path
import json

router = APIRouter()


@router.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    """
    Get the status of a Celery task.
    """
    task_result = AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }