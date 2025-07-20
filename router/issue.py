import os
from typing import List, Optional
import uuid

from fastapi.responses import FileResponse
from db.config import SessionLocal
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from model.role import Role
from router.auth import get_current_user, get_current_user_id, require_role
from router.require_role import get_all_roles_dependency
from schema.issue import IssueApproveReject, IssueDelete, IssueEdit, IssueImageDelete, IssueUpdate
from schema.permission import PermissionRead, PermissionCreate, PermissionUpdate, PermissionDelete
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from crud.issue import UPLOAD_DIR, approveIssue, create_multiple_uploads, delete_issue, deleteImage, get_issues, get_issues_logs, getIssue, master_data, rejectIssue, update_issue, update_multiple_uploads

router = APIRouter()
security = HTTPBearer()
#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwcmVldGhpQGdtYWlsLmNvbSIsInJvbGVzIjpbIkFkbWluIl0sImV4cCI6MTc0MDU2MjAyMH0.UJQmEnYKqgicGHJifNOpx5j6ZI_9iUGO3ZSYKr2XMGw

ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
ALGORITHM = "HS256"
password_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")


def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
        

        
@router.get("/masterData/", response_model = '', dependencies=[Depends(get_all_roles_dependency)])
def get_master_data(skip : int = 0 , limit: int = 10, db : Session = Depends(get_db)): 
    # here get_roles is variable
    return master_data(db = db , skip = skip , limit = limit)

@router.post("/create-task", response_model='', dependencies=[Depends(get_all_roles_dependency)])
async def create_task(title: str = Form(...),description: str = Form(...),type: str = Form(...),state: str = Form(...),azure_ticket_no: str = Form(...),priority: str = Form(...),user_id:str = Form(...),files: Optional[List[UploadFile]] = File(None),db: Session = Depends(get_db)):
    saved_files = []
    if files :
        for file in files:
            contents = await file.read()
            file_id = uuid.uuid4()
            file_name = file.filename
            ext = os.path.splitext(file_name)[1]
            file_size = len(contents)
            full_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file_name}")

            with open(full_path, "wb") as f:
                f.write(contents)

            saved_files.append({
                "id": file_id,
                "file_name": file_name,
                "ext": ext.lstrip("."),
                "path": full_path,
                "file_size": file_size
            })

    result = create_multiple_uploads(db=db,
        title=title,
        description=description,
        type=type,
        state=state,
        azure_ticket_no=azure_ticket_no,
        priority=priority,
        created_by= user_id,
        files=saved_files
    )
    
    #print(get_current_user())

    return result

@router.get("/getAllIssues", response_model='',  dependencies=[Depends(get_all_roles_dependency)])
def get_all_issues(skip : int = 0 , limit: int = 10, db : Session = Depends(get_db)):
    return get_issues(db = db , skip = skip , limit = limit)

@router.post('/getIssue', response_model='', dependencies=[Depends(get_all_roles_dependency)])
def getIssueById(issue: IssueEdit, db: Session = Depends(get_db)):
    return getIssue(db=db, issue=issue)

@router.get("/download/{filename}", response_model='', dependencies=[Depends(get_all_roles_dependency)])
def download_file(filename: str):
    # Prevent directory traversal attacks
    if ".." in filename or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    raise HTTPException(status_code=404, detail="File not found")

@router.post("/approve-issue", response_model='', dependencies=[Depends(get_all_roles_dependency)])
def approve_issue(issue: IssueApproveReject, db: Session = Depends(get_db)):
    #print(issue)
    #return issue
    return approveIssue(issue=issue, db=db)

@router.post("/reject-issue", response_model='', dependencies=[Depends(get_all_roles_dependency)])
def reject_issue(issue: IssueApproveReject, db: Session = Depends(get_db)):
    return rejectIssue(issue=issue, db=db)

@router.post("/deleteIssue", response_model='', dependencies=[Depends(get_all_roles_dependency)])
def delete_file(image: IssueImageDelete, db: Session = Depends(get_db)):
    return deleteImage(image=image, db=db)


@router.post("/update-task", response_model='', dependencies=[Depends(get_all_roles_dependency)])
async def update_task(issue: IssueUpdate, db: Session = Depends(get_db)):
    result = update_issue(issue=issue, db=db)
    return result

@router.post("/update-attachments", response_model='', dependencies=[Depends(get_all_roles_dependency)])
async def update_attachments(id: str = Form(...),user_id:str = Form(...),files: List[UploadFile] = File(...),db: Session = Depends(get_db)):
    saved_files = []

    for file in files:
        contents = await file.read()
        file_id = uuid.uuid4()
        file_name = file.filename
        ext = os.path.splitext(file_name)[1]
        file_size = len(contents)
        full_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file_name}")

        with open(full_path, "wb") as f:
            f.write(contents)

        saved_files.append({
            "id": file_id,
            "file_name": file_name,
            "ext": ext.lstrip("."),
            "path": full_path,
            "file_size": file_size
        })

    result = update_multiple_uploads(db=db,
        id=id,
        created_by= user_id,
        files=saved_files
    )
    
    #print(get_current_user())

    return result

@router.post("/delete-issue", response_model='', dependencies=[Depends(get_all_roles_dependency)])
async def delete_task(issue: IssueDelete, db: Session = Depends(get_db)):
    result = delete_issue(issue=issue, db=db)
    return result

@router.get("/getAllIssueLog/{issueId}", response_model='',  dependencies=[Depends(get_all_roles_dependency)])
def get_all_issues_log(issueId: str, skip : int = 0 , limit: int = 10, db : Session = Depends(get_db)):
    return get_issues_logs(db = db , skip = skip , limit = limit, issueId = issueId)