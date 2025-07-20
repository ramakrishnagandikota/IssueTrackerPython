from fastapi.security import OAuth2PasswordBearer
from db.config import SessionLocal
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from router.require_role import get_all_roles_dependency
from schema.user import UserRead, UserCreate, UserUpdate, UserDelete, UserSearch
from sqlalchemy.orm import Session
from crud.user import delete_user_id, read_users, read_user_id, post_user,update_user_id,userSearch # , , update_user_id,delete_user_id
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional,List
from jose import jwt, JWTError
from router.auth import require_role
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


router = APIRouter()
#security = HTTPBearer()

ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
ALGORITHM = "HS256"
password_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
#oauth2_schema = OAuth2PasswordBearer(tokenUrl="/", auto_error=True)

def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
        
@router.get("/users/", response_model = '', dependencies=[Depends(get_all_roles_dependency)])
def get_users(skip : int = 0 , limit: int = 10, db : Session = Depends(get_db)): 
    # here get_roles is variable
    return read_users(db = db , skip = skip , limit = limit)      

@router.post("/user/", response_model = '')
def create_user(user : UserCreate, db : Session = Depends(get_db)):
    return post_user(db = db , user = user)

@router.get("/users/{id}", response_model = UserRead,dependencies=[Depends(get_all_roles_dependency)])
def get_user(id : str, db: Session = Depends(get_db)):
    return read_user_id(db = db , user_id = id  )

@router.post("/user/update", response_model = '',dependencies=[Depends(get_all_roles_dependency)])
def update_user(user : UserUpdate , db: Session = Depends(get_db)):
    return update_user_id(user = user, db = db)

@router.post("/user/delete", response_model= '', dependencies=[Depends(get_all_roles_dependency)])
def delete_user(user :UserDelete, db: Session = Depends(get_db)):
    return delete_user_id(db = db, user = user)

@router.post('/user/search')
def user_search(search: UserSearch, db: Session = Depends(get_db), skip: int = 0,limit: int = 10):
    return userSearch(search=search, db = db, skip=skip, limit=limit)
