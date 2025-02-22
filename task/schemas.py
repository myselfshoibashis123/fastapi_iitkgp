from pydantic import BaseModel

class TaskCreate(BaseModel):
    resource_id: str  # Only require the resource_id
    model_type: str
    class Config():
        #orm_mode = True as 'orm_mode' has been renamed to 'from_attributes'
        from_attributes = True

