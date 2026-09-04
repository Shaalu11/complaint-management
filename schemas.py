from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Student(BaseModel):
    id: int
    name: str
    email: str
    room_number: str

#Student creates this
class ComplaintCreate(BaseModel):
    title:str
    description:str
    category:str
    student_id:int

#API sends this back
class ComplaintResponse(BaseModel):
    id:int
    title:str
    description:str
    category:str
    student_id:int
    status:str
    created_at:Optional[datetime] = None
    updated_at:Optional[datetime] = None



