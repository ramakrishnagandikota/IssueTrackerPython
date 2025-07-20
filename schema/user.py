from typing import Optional
from pydantic import BaseModel  
from datetime import datetime
from uuid import UUID
from schema.role import GetRole


class UserBase(BaseModel):
    id: UUID   
    first_name : str
    last_name : str
    email : str 
    mobile_number : str 
    #password : str 
    address : str 
    date_of_birth : Optional[str] 
    profile_picture : Optional[str] 
    status : int
    role : list[GetRole]
    
class UserCreate(BaseModel):
    first_name : str
    last_name : str
    email : str 
    mobile_number : str 
    password : str 
    address : str 
    date_of_birth : Optional[str] 
    profile_picture : Optional[str]
    status : int
    role_id : UUID
    
class UserRead(UserBase): 
    created_at : datetime
    updated_at : datetime
    
class UserUpdate(BaseModel):
    id: UUID
    first_name : str
    last_name : str
    email : str 
    mobile_number : str 
    address : Optional[str]
    date_of_birth : Optional[str] 
    profile_picture : Optional[str] 
    status : int
    role_id : UUID

class UserDelete(BaseModel):
    id : UUID
    user_id: UUID

class UserSearch(BaseModel):
    search: str
    
class UserSafe(BaseModel):
    id: UUID   
    first_name : str
    last_name : str
    email : str 
    mobile_number : str 
    address : str 
    date_of_birth: Optional[str] = None
    profile_picture: Optional[str] = None
    status : int
    
    class Config:
        from_attributes = True  # Ensure ORM mode is enabled7
    