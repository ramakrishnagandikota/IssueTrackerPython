from db.config import SessionLocal
from fastapi import APIRouter, Depends
from router.auth import require_role
from router.require_role import get_all_roles_dependency
from schema.permission import PermissionRead, PermissionCreate, PermissionUpdate, PermissionDelete
from sqlalchemy.orm import Session
from crud.permission import read_permissions, post_permission, read_permission_id, update_permission_id,delete_permission_id
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
        
@router.get("/permissions/", response_model = list[PermissionRead], dependencies=[Depends(get_all_roles_dependency)])
def get_permissions(skip : int = 0 , limit: int = 10, db : Session = Depends(get_db)): 
    # here get_roles is variable
    return read_permissions(db = db , skip = skip , limit = limit)      

@router.post("/permission/", response_model = PermissionRead)
def create_permission(permission : PermissionCreate, db : Session = Depends(get_db)):
    return post_permission(db = db , permission = permission)

@router.get("/permission/{id}", response_model = PermissionRead, dependencies=[Depends(get_all_roles_dependency)])
def get_permission(id : str, db: Session = Depends(get_db)):
    return read_permission_id(db = db , permission_id = id  )

@router.post("/permission/update", response_model = PermissionRead, dependencies=[Depends(get_all_roles_dependency)])
def update_permission(permission : PermissionUpdate , db: Session = Depends(get_db)):
    return update_permission_id(role = permission, db = db)

@router.post("/permission/delete", response_model= PermissionRead, dependencies=[Depends(get_all_roles_dependency)])
def delete_permission(id :PermissionDelete, db: Session = Depends(get_db)):
    return delete_permission_id(db = db, permission = id)