from typing import List, Optional
from pydantic import BaseModel  
from datetime import datetime
from uuid import UUID

from schema.permission import GetPermissions


class RoleBase(BaseModel):
    id: UUID   
    role_name : str
    description : str 
    status : int
    
class GetRole(BaseModel):
    id: Optional[UUID]
    role_name: Optional[str]
    
class RoleCreate(BaseModel):
    role_name : str
    description : str 
    status : int
    permission_id: List[UUID]
    
class RoleRead(RoleBase): 
    created_at : datetime
    updated_at : datetime
    permissions: List[GetPermissions]
    
class RoleUpdate(BaseModel):
    id: UUID
    role_name: str
    description: str
    status: int
    permission_id: List[UUID]

class RoleDelete(BaseModel):
    id : UUID
    user_id: UUID

    class Config:
        from_attributes = True  # Ensure ORM mode is enabled7
        from_attributes = True
    