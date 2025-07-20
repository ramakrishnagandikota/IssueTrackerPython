from typing import Optional
from pydantic import BaseModel  
from datetime import datetime
from uuid import UUID


class AuthBase(BaseModel):
    email: str
    password : str 
    

    class Config:
        from_attributes = True  # Ensure ORM mode is enabled7
        orm_mode = True