from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from datetime import datetime
import uuid
from uuid import uuid4




class FileUpload(Base):
    __tablename__ = "Asset_Data"

    # Columns
    resource_id = Column(String, primary_key=True, index=True)  # Primary Key
    resource_name = Column(String, nullable=False)
    resource_description = Column(String, nullable=False)  #Description
    resource_type_file = Column(String, nullable=False, default="True")  # Always True
    resource_location = Column(String, nullable=False)  #Path where the file is stored
    updated_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # timestamp
    tasks = relationship("Task", back_populates="file")


class Task(Base):
    __tablename__ = "Task_Data"

    task_id = Column(String, primary_key=True, index=True)
    resource_id = Column(String, ForeignKey("Asset_Data.resource_id"), nullable=False)
    task_name = Column(String, nullable=False)
    task_description = Column(String, nullable=True)
    task_status = Column(String, default="Pending")
    priority = Column(String, nullable=True, default="NULL")
    created_on = Column(DateTime, default=datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    model_type = Column(String, nullable=True)
    # New columns for ML metrics
    accuracy = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)

    file = relationship("FileUpload", back_populates="tasks")

