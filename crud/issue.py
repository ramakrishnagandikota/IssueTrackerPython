import os
from typing import List, Optional

from fastapi import File, UploadFile
from sqlalchemy import desc, func
from model.issue_log import IssueLog
from model.issues_attachments import IssueAttachments
from model.permission import Permission
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.inspection import inspect
import uuid
from model.issue import Issue
from model.type import Type
from model.state import State
from model.priority import Priority
from model.user import User
from schema.issue import IssueApproveReject, IssueDelete, IssueEdit, IssueImageDelete, IssueUpdate

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def master_data(db: Session, skip : int = 0, limit: int = 10 ):
    type_data = db.query(Type).order_by(Type.created_at).offset(skip).limit(limit).all()
    priority_data = db.query(Priority).order_by(Priority.created_at).offset(skip).limit(limit).all()
    state_data = db.query(State).order_by(State.created_at).offset(skip).limit(limit).all()
    return {
        'type': type_data,
        'priority': priority_data,
        'state': state_data
    }

def create_multiple_uploads(db: Session,
    title: str,
    description: str,
    type: str,
    state: str,
    azure_ticket_no: str,
    priority: str,
    created_by: uuid,
    files: list[dict]):
    
    issue_record = db.query(Issue).filter(Issue.title == title).first()
    if issue_record:
        return{
            "status": "Fail",
            "message" : "This issue is already created with this title."
        }
    issue_id = uuid.uuid4()
    issue = Issue(id=issue_id, title=title, description=description, type= type, state=state, azure_ticket_no=azure_ticket_no,priority=priority, created_by=created_by)
    db.add(issue)

    create_log(created_by,issue_id,'create_multiple_uploads','',db=db)
    # Step 2: Save each attachment
    if files:
        for file in files:
            
            attachment = IssueAttachments(
                id=file["id"],
                issues_id=issue_id,
                file_name=file["file_name"],
                ext=file["ext"],
                path=file["path"],
                size= file['file_size'],
                created_by=created_by,
                updated_by=created_by
            )
            db.add(attachment)
            create_log(created_by,issue_id,'create_multiple_uploads_images',file["file_name"],db=db)
            pass
        db.commit()
        db.flush()

    return {"status": "Success","message": "Task created successfully", "task_id": issue_id}

def get_issues(db: Session, skip : int = 0, limit: int = 10):
    issues = (
        db.query(Issue, Type.type_name, State.state_name, Priority.priority_name)
        .join(Type, Type.id == Issue.type)
        .join(State, State.id == Issue.state)
        .join(Priority, Priority.id == Issue.priority)
        #.options(joinedload(Issue.attachments))
        .filter(Issue.deleted == False)
        .order_by(desc(Issue.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for issue, type_name, state_name, priority_name in issues:
        #attachments = db.query(IssueAttachments).filter_by(issues_id=issue.id).all()
        # result.append({
        #     "issue": {k: v for k, v in issue.__dict__.items()},
        #     "type_name": type_name,
        #     "state_name": state_name,
        #     "priority_name": priority_name
        # })
        
        data = {
            "id" : issue.id,
            "title" : issue.title,
            "description" : issue.description,
            "state" : issue.state,
            "azure_ticket_no" : issue.azure_ticket_no,
            "created_at" : issue.created_at,
            "created_by" : issue.created_by,
            "status" : issue.status,
            "updated_at" : issue.updated_at,
            "type_name" : type_name,
            "state_name" : state_name,
            "priority_name" : priority_name,
            "attachments" : issue.attachments,
            
        }
        
        result.append(data)
    return result

def getIssue(issue: IssueEdit, db=Session):
    issue_record = db.query(Issue).filter(Issue.id == issue.id).first()

    if not issue_record:
        return None  # or raise an HTTPException if using FastAPI

    userCreated = db.query(User).filter(User.id == issue_record.created_by).first()
    userUpdated = db.query(User).filter(User.id == issue_record.updated_by).first()

    return {
        "id": issue_record.id,
        "title": issue_record.title,
        "description": issue_record.description,
        "type": issue_record.type,
        "state": issue_record.state,
        "priority": issue_record.priority,
        "azure_ticket_no": issue_record.azure_ticket_no,
        "status": issue_record.status,
        "created_at": issue_record.created_at,
        "updated_at": issue_record.updated_at,
        "created_by": f"{userCreated.first_name} {userCreated.last_name}" if userCreated else None,
        "updated_by": f"{userUpdated.first_name} {userUpdated.last_name}" if userUpdated else None,
        "attachments": issue_record.attachments
    }

def approveIssue(issue: IssueApproveReject, db: Session):
    issueDB = db.query(Issue).filter(Issue.id == issue.id).first()
    #state = db.query(State).filter(State.state_name == issue.state).first()
    #print(issue)
    if issueDB:
        issueDB.status = 1
        db.commit()
        db.refresh(issueDB)
        create_log(issue.user_id,issueDB.id,'approveIssue','',db=db)
        return {
            "status" : "Success",
            "message" : "Issue approved successfully"
        }
    else:
        return None
    
def rejectIssue(issue: IssueApproveReject, db: Session):
    issueDB = db.query(Issue).filter(Issue.id == issue.id).first()
    #state = db.query(State).filter(State.state_name == issue.state).first()
    if issueDB:
        issueDB.status = 0
        db.commit()
        db.refresh(issueDB)
        create_log(issue.user_id,issueDB.id,'rejectIssue','',db=db)
        return {
            "status" : "Success",
            "message" : "Issue rejected successfully"
        }
    else:
        return None
    
def deleteImage(image: IssueImageDelete, db: Session):
    delete = db.query(IssueAttachments).filter(IssueAttachments.id == image.id).first()
    if delete:
        file_path = delete.path
        if os.path.exists(file_path):
            os.remove(file_path)
        db.delete(delete)
        db.commit()
        create_log(image.user_id,image.issue_id,'deleteImage',delete.file_name,db=db)
        return {
            "status": "Success",
            "message": "Image deleted successfully."
        }
    else:
        return {
            "status" : "Fail",
            "message" : "Unable to delete image."
        }
    
def update_issue(issue: IssueUpdate, db: Session):
    issue_update = db.query(Issue).filter(Issue.id == issue.id).first()
    if issue_update:
        for key, value in issue.dict(exclude={"user_id"}).items():
            setattr(issue_update, key, value)
        
        # Set updated_by field with the user_id
        issue_update.updated_by = issue.user_id

        db.commit()
        db.refresh(issue_update)
        create_log(issue.user_id,issue_update.id,'update_issue','',db=db)
        return {
            "status": "Success",
            "message": "Issue updated successfully."
        }
    else:
        return {
            "status": "Fail",
            "message": "Unable to update issue."
        }

def update_multiple_uploads(db: Session,
    id: str,
    created_by: uuid,
    files: list[dict]):

    # Step 2: Save each attachment
    for file in files:
        attachment = IssueAttachments(
            id=file["id"],
            issues_id=id,
            file_name=file["file_name"],
            ext=file["ext"],
            path=file["path"],
            size= file['file_size'],
            created_by=created_by,
            updated_by=created_by
        )
        create_log(created_by,id,'update_multiple_uploads',file['file_name'],db=db)
        db.add(attachment)

    db.commit()
    db.flush()

    return {"status": "Success","message": "Task created successfully"}

def delete_issue(issue: IssueDelete, db: Session):
    issueDB = db.query(Issue).filter(Issue.id == issue.id).first()
    if issueDB:
        issueDB.deleted = True
        issueDB.deleted_at = func.now()
        issueDB.deleted_by = issue.user_id
        db.commit()
        db.refresh(issueDB)
        create_log(issue.user_id,issueDB.id,'delete_issue','',db=db)
        return {
            "status" : "Success",
            "message" : "Issue deleted successfully"
        }
    else:
        return None
    
def get_issues_logs(db: Session, skip : int = 0, limit: int = 10, issueId: str = ''):
    logs = (
        db.query(IssueLog.log_name, IssueLog.issues_id, IssueLog.created_at)
        .filter(IssueLog.issues_id == issueId)
        .filter(IssueLog.deleted == False)
        .order_by(desc(IssueLog.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = [
        {
            "log_name": log.log_name,
            "issues_id": log.issues_id,
            "created_at": log.created_at
        }
        for log in logs
    ]
    return result
    
def create_log(user_id: uuid, issue_id: uuid, method: str, name: str, db: Session):
    user = db.query(User.first_name, User.last_name).filter(User.id == user_id).first()
    message = ''
    if method == 'create_multiple_uploads':
        message = f"{user.first_name} {user.last_name} has created an issue"
    elif method == 'approveIssue':
        message = f"{user.first_name} {user.last_name} has approved this issue"
    elif method == 'rejectIssue':
        message = f"{user.first_name} {user.last_name} has rejected this issue"
    elif method == 'deleteImage':
        message = f"{user.first_name} {user.last_name} has deleted the issue file: {name}"
    elif method == 'update_issue':
        message = f"{user.first_name} {user.last_name} has updated the issue"
    elif method == 'update_multiple_uploads':
        message = f"{user.first_name} {user.last_name} has uploaded the file: {name}"
    elif method == 'delete_issue':
        message = f"{user.first_name} {user.last_name} has deleted the issue"
    elif method == 'create_multiple_uploads_images':
        message = f"{user.first_name} {user.last_name} has uploaded the file: {name}"

    if message:
        log = IssueLog(
            id=uuid.uuid4(),
            log_name=message,
            issues_id=issue_id,
            created_by=user_id
        )
        db.add(log)
        db.commit()
        db.refresh(log)
    