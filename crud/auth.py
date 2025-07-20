from model.permission import Permission
from schema.user import UserSafe
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from model.user import User, UserRole
from model.role import Role, RolePermission
import uuid
from fastapi import HTTPException

def getUser(db: Session, email: str) -> UserSafe:
    return db.query(User).filter(User.email == email).first()

def getUserRoles(db : Session, user_id : str):
    return db.query(Role).join(UserRole).filter(UserRole.user_id == user_id).all()

def getRolePerissions(db : Session, role_id : str):
    role = db.query(Role).filter(Role.role_name == role_id).first()
    return db.query(Permission).join(RolePermission).filter(RolePermission.role_id == role.id).all()