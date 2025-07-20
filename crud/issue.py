import os

from sqlalchemy import desc, func
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
from schema.issue import IssueDelete, IssueEdit, IssueUpdate

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
    
    issue_id = uuid.uuid4()
    issue = Issue(id=issue_id, title=title, description=description, type= type, state=state, azure_ticket_no=azure_ticket_no,priority=priority, created_by=created_by)
    db.add(issue)

    # Step 2: Save each attachment
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

def approveIssue(issue: IssueEdit, db: Session):
    issueDB = db.query(Issue).filter(Issue.id == issue.id).first()
    #state = db.query(State).filter(State.state_name == issue.state).first()
    #print(issue)
    if issueDB:
        issueDB.status = 1
        db.commit()
        db.refresh(issueDB)
        return {
            "status" : "Success",
            "message" : "Issue approved successfully"
        }
    else:
        return None
    
def rejectIssue(issue: IssueEdit, db: Session):
    issueDB = db.query(Issue).filter(Issue.id == issue.id).first()
    #state = db.query(State).filter(State.state_name == issue.state).first()
    if issueDB:
        issueDB.status = 0
        db.commit()
        db.refresh(issueDB)
        return {
            "status" : "Success",
            "message" : "Issue rejected successfully"
        }
    else:
        return None
    
def deleteImage(id: str, db: Session):
    delete = db.query(IssueAttachments).filter(IssueAttachments.id == id).first()
    if delete:
        file_path = delete.path
        if os.path.exists(file_path):
            os.remove(file_path)
        db.delete(delete)
        db.commit()
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
        return {
            "status" : "Success",
            "message" : "Issue deleted successfully"
        }
    else:
        return None