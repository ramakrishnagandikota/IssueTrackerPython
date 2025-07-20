import base64
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2, OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.config import SessionLocal
from crud.auth import getRolePerissions, getUser,getUserRoles
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional,List
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from model.user import User
from schema.user import UserSafe

router = APIRouter()
security = HTTPBearer()
#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwcmVldGhpQGdtYWlsLmNvbSIsInJvbGVzIjpbIkFkbWluIl0sImV4cCI6MTc0MDU2MjAyMH0.UJQmEnYKqgicGHJifNOpx5j6ZI_9iUGO3ZSYKr2XMGw

ACCESS_TOKEN_EXPIRE_HOURS = 1
SECRET_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
ALGORITHM = "HS256"
password_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
        
@router.post("/login")
def login(payload: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # hashed_password = password_context.hash(payload.password)
    # return hashed_password
    
    username_bytes = base64.b64decode(payload.username)
    username = username_bytes.decode('utf-8')
    password_bytes = base64.b64decode(payload.password)
    password = password_bytes.decode('utf-8')
    user = getUser(db= db, email = username)
    #print(user)
    if user:
        if verify_password(password, user.password):
    #if not user or verify_password(password, user.password):
            roles = [role.role_name for role in getUserRoles(db=db, user_id = user.id)]
            access_token = create_access_token({"sub": user.email, "roles": roles})
            roles_string = roles[0] if roles else ""
            if roles_string :
                permissions = [permission.permission_name for permission in getRolePerissions(db=db, role_id = roles_string)]
            else :
                permissions = []
            return {
                "status" : "Success",
                "user" : UserSafe.from_orm(user),
                "role" : roles,
                "permissions": permissions,
                "access_token" : access_token,
                "token_type" : "Bearer",
                "expiry" : ACCESS_TOKEN_EXPIRE_HOURS
            }
        else:
            raise HTTPException(status_code=401, detail= {"status" : "Fail", "message" : "Invalid credentials"})
    else:
        return {
                "status" : "Fail",
                "message" : "The Email & password entered doesn't exist."
                }
    
    
def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)
    
def create_access_token(data: dict, expires: Optional[timedelta] =  None):
    to_encode = data.copy()
    expiry = datetime.utcnow() + (expires or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expiry})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials  # Extract token from header
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # ✅ Fixed algorithms=[ALGORITHM]
        username: str = payload.get('sub')
        roles: List[str] = payload.get('roles', [])
        exp: int = payload.get('exp')

        # ✅ Check token expiration
        if datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expired")

        # ✅ Check if username exists
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        # ✅ Get user from DB
        user = getUser(db=db, email=username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return {"user": user, "roles": roles}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")        

def require_role(required_roles: List[str]):
    def role_checker(user_data = Depends(get_current_user)):
        user_roles = user_data["roles"]
        print(user_roles)
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Permission denied")
        return user_data
    return role_checker

def get_current_user_id(token: str = Depends(oauth2_schema)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")