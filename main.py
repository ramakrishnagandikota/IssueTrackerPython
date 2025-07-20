from fastapi import FastAPI, APIRouter
from db.config import Base, engine
from model.priority import Priority
from model.role import Role, RolePermission
from model.state import State
from model.type import Type
from model.user import User, UserRole
from model.issues_attachments import IssueAttachments
from model.issues_state_history import IssueStateHistory
from router import user
from router import role
from router import permission
from router import auth
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event
from sqlalchemy.orm import Session
from db.config import engine, Base, SessionLocal
from model.permission import Permission  # adjust path if needed
import uuid
from router import issue
from model.issue_log import IssueLog


@event.listens_for(Base.metadata, "after_create")
def insert_default_permissions(target, connection, **kw):
    db = Session(bind=connection)
    # inserting permissions
    pid1 = uuid.uuid4()
    pid2 = uuid.uuid4()
    pid3 = uuid.uuid4()
    pid4 = uuid.uuid4()
    pid5 = uuid.uuid4()
    pid6 = uuid.uuid4()
    default_permissions = [
        Permission(id=pid1, permission_name="Users", description="Users", status=1),
        Permission(id=pid2, permission_name="Roles", description="Roles", status=1),
        Permission(id=pid3, permission_name="Permissions", description="Permissions", status=1),
        Permission(id=pid4, permission_name="Dashboard", description="Dashboard", status=1),
        Permission(id=pid5, permission_name="Issues", description="Issues", status=1),
        Permission(id=pid6, permission_name="Reviews", description="Reviews", status=1),
    ]
    
    existing1 = db.query(Permission).count()
    if existing1 == 0:
        db.add_all(default_permissions)
        db.commit()
    
    # inserting roles
    role_id = uuid.uuid4()
    default_roles = [
        Role(id=role_id, role_name="Admin", description="Admin", status=1)
    ]
    existing2 = db.query(Role).count()
    if existing2 == 0:
        db.add_all(default_roles)
        db.commit()
    
    # inserting roles with permissions
    default_permissions = [
        RolePermission(id=uuid.uuid4(), role_id= role_id, permission_id = pid1),
        RolePermission(id=uuid.uuid4(), role_id= role_id, permission_id = pid2),
        RolePermission(id=uuid.uuid4(), role_id= role_id, permission_id = pid3),
        RolePermission(id=uuid.uuid4(), role_id= role_id, permission_id = pid4),
        RolePermission(id=uuid.uuid4(), role_id= role_id, permission_id = pid5),
        RolePermission(id=uuid.uuid4(), role_id= role_id, permission_id = pid6),
    ]
    existing3 = db.query(RolePermission).count()
    if existing3 == 0:
        db.add_all(default_permissions)
        db.commit()
    
    user_id = uuid.uuid4()
    default_users = [
        User(id=user_id, first_name="Ripple", last_name="Metering", email="ripple@gmail.com", password="$2b$12$LIUMz.z6fJwNXXD0QPALTOnUxLyuWln3tDX4XnIEnAwSAk4sa9owu", mobile_number="9000000000", address="ripple", status=1),
    ]
    existing4 = db.query(User).count()
    if existing4 == 0:
        db.add_all(default_users)
        db.commit()
        
    user_roles = [
        UserRole(id=uuid.uuid4(), user_id=user_id, role_id=role_id)
    ]
    existing5 = db.query(UserRole).count()
    if existing5 == 0:
        db.add_all(user_roles)
        db.commit()
        
    # Adding data to state
    state_data = [
        # State(id=uuid.uuid4(),state_name="In Review", description="In Review",status=1),
        # State(id=uuid.uuid4(),state_name="Approved", description="Approved",status=1),
        # State(id=uuid.uuid4(),state_name="Rejected", description="Rejected",status=1),
        State(id=uuid.uuid4(),state_name="Todo", description="Todo",status=1),
        State(id=uuid.uuid4(),state_name="Development", description="Development",status=1),
        State(id=uuid.uuid4(),state_name="Done", description="Done",status=1),
    ]
    existing6 = db.query(State).count()
    if existing6 == 0:
        db.add_all(state_data)
        db.commit()
        
    # Adding data to type
    type_data = [
        Type(id=uuid.uuid4(), type_name="Bug", description="Bug", status=1),
        Type(id=uuid.uuid4(), type_name="Feature", description="Feature", status=1),
        Type(id=uuid.uuid4(), type_name="Enhancement", description="Enhancement", status=1),
    ]
    existing7 = db.query(Type).count()
    if existing7 == 0:
        db.add_all(type_data)
        db.commit()
        
    # Adding data to Priority
    priority_data = [
        Priority(id=uuid.uuid4(), priority_name="Low", description="Low", status=1),
        Priority(id=uuid.uuid4(), priority_name="Medium", description="Medium", status=1),
        Priority(id=uuid.uuid4(), priority_name="High", description="High", status=1),
    ]
    existing8 = db.query(Priority).count()
    if existing8 == 0:
        db.add_all(priority_data)
        db.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(
docs_url="/swagger",  # Custom path for Swagger UI
redoc_url=None  
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/api", tags=["users"]),
app.include_router(role.router, prefix="/api", tags=["roles"]),
app.include_router(permission.router, prefix="/api", tags=["permissions"]),
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(issue.router, prefix="/api", tags=["issue"])