from schema.permission import PermissionCreate, PermissionUpdate, PermissionDelete
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from model.permission import Permission
import uuid

def read_permissions(db: Session, skip : int = 0, limit: int = 10 ): 
   permissions =  db.query(Permission).order_by(Permission.permission_name).offset(skip).limit(limit).all()
   return permissions

def post_permission(db : Session, permission: PermissionCreate):
   permission  = Permission(id = uuid.uuid4(),**permission.dict())
   db.add(permission)
   db.commit()
   db.refresh(permission)
   return permission

def read_permission_id(db: Session, permission_id : str):
   permission = db.query(Permission).filter(Permission.id == permission_id).first()
   return permission

def update_permission_id(db:Session , permission: PermissionUpdate):
   permission_update = db.query(Permission).filter(Permission.id == permission.id).first()
   if permission_update: 
      # user_dict = object_to_dict(user)
      for key, value in permission.dict().items():
         setattr(permission_update,key,value)
      db.commit()
      db.refresh(permission_update)
   return permission_update


def delete_permission_id(db : Session, permission : PermissionDelete): 
   permission_delete = db.query(Permission).filter(Permission.id == permission.id).first()
   if permission_delete:
      db.delete(permission_delete)
      db.commit()
   return permission_delete