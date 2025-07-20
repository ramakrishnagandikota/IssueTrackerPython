from typing import Optional
from pydantic import BaseModel  
from datetime import datetime
from uuid import UUID



class IssueBase(BaseModel):
    id: UUID   
    title : str
    description : str
    
class IssueEdit(BaseModel):
    id: UUID
    
class IssueFile(BaseModel):
    fileName: str
    
class IssueApproveReject(BaseModel):
    id: UUID
    state: str
    
class IssueUpdate(BaseModel):
    id: UUID   
    title : str
    description : str
    state: UUID
    type: UUID
    priority: UUID
    azure_ticket_no: str
    user_id: UUID
    
class IssueDelete(BaseModel):
    id: UUID
    user_id: UUID