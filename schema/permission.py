from typing import Optional
from pydantic import BaseModel  
from datetime import datetime
from uuid import UUID


class PermissionBase(BaseModel):
    id: UUID   
    permission_name : str
    description : str 
    status : int
    
class GetPermission(BaseModel):
    id: Optional[UUID]
    permission_name: Optional[str]
    
class PermissionCreate(BaseModel):
    permission_name : str
    description : str 
    status : int
    
class PermissionRead(PermissionBase): 
    created_at : datetime
    updated_at : datetime
    
class PermissionUpdate(PermissionBase):
    pass

class GetPermissions(BaseModel):
    id: Optional[UUID]
    permission_name: Optional[str]

class PermissionDelete(BaseModel):
    id : UUID

    class Config:
        from_attributes = True  # Ensure ORM mode is enabled7
    