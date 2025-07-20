from db.config import SessionLocal
from fastapi import APIRouter, Depends
from model.role import Role
from router.auth import require_role
from router.require_role import get_all_roles_dependency
from schema.role import RoleRead, RoleCreate, RoleUpdate, RoleDelete
from sqlalchemy.orm import Session
from crud.role import read_roles, post_role, read_role_id, update_role_id,delete_role_id
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

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
        
@router.get("/roles/", response_model = list[RoleRead], dependencies=[Depends(get_all_roles_dependency)])
def get_roles(skip : int = 0 , limit: int = 10, db : Session = Depends(get_db)): 
    # here get_roles is variable
    return read_roles(db = db , skip = skip , limit = limit)      

@router.post("/role/", response_model = '')
def create_role(role : RoleCreate, db : Session = Depends(get_db)):
    return post_role(db = db , role = role)

@router.get("/roles/{id}", response_model = RoleRead, dependencies=[Depends(get_all_roles_dependency)])
def get_role(id : str, db: Session = Depends(get_db)):
    return read_role_id(db = db , role_id = id  )

@router.post("/role/update", response_model = '', dependencies=[Depends(get_all_roles_dependency)])
def update_role(role : RoleUpdate , db: Session = Depends(get_db)):
    return update_role_id(role = role, db = db)

@router.post("/role/delete", response_model= '', dependencies=[Depends(get_all_roles_dependency)])
def delete_role(role :RoleDelete, db: Session = Depends(get_db)):
    return delete_role_id(db = db, role = role)

def get_all_roles(db: Session = Depends(get_db)):
    roles = db.query(Role.role_name).all()
    role_names = [r.role_name for r in roles]
    return require_role(role_names)