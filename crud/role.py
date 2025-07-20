from sqlalchemy import func
from model.permission import Permission
from schema.role import RoleCreate, RoleUpdate, RoleDelete
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from model.role import Role, RolePermission
import uuid

def read_roles(db: Session, skip : int = 0, limit: int = 10 ): 
   roles =  db.query(Role).filter(Role.deleted == False).order_by(Role.created_at).offset(skip).limit(limit).all()
   return roles

def post_role(db : Session, role: RoleCreate):
   checkRole = db.query(Role).filter(Role.role_name == role.role_name).filter(Role.deleted == False).first()
   if checkRole:
      return {
         'status': "Fail",
         'message': "Role already created"
      }
   else :
      new_role = Role(
         id=uuid.uuid4(),
         role_name=role.role_name,
         description=role.description,
         status=role.status
      )
      db.add(new_role)
      db.flush()  # Ensure new_role.id is available

      for perm_id in role.permission_id:
         link = RolePermission(
            id=uuid.uuid4(),
            role_id=new_role.id,
            permission_id=perm_id
         )
         db.add(link)

      db.commit()
      db.refresh(new_role)

      return {
         'status': "Success",
         'message': "Role created successfully"
      }

def read_role_id(db: Session, role_id : str):
   role = db.query(Role).filter(Role.id == role_id).first()
   return role

# def update_role_id(db:Session , role: RoleUpdate):
#    role_update = db.query(Role).filter(Role.id == role.id).first()
#    if role_update: 
#       # user_dict = object_to_dict(user)
#       for key, value in role.dict().items():
#          setattr(role_update,key,value)
#       db.commit()
#       db.refresh(role_update)
#    return role_update

def update_role_id(db: Session, role: RoleUpdate):
    role_update = db.query(Role).filter(Role.id == role.id).first()
    if not role_update:
        return {
           "status" : "Fail",
           "message" : "No role exixts with this name"
        }

    # Update role fields (excluding permissions)
    for key, value in role.dict(exclude={"permission_id"}).items():
        setattr(role_update, key, value)

    # Delete existing RolePermission mappings
    db.query(RolePermission).filter(RolePermission.role_id == role.id).delete()

    # Insert new RolePermission mappings
    for perm_id in role.permission_id:
        db.add(RolePermission(role_id=role.id, permission_id=perm_id))

    db.commit()
    db.refresh(role_update)
    return {
       "status": "Success",
       "message": "Role updated successfully"
    }


def delete_role_id(db : Session, role : RoleDelete): 
   role_delete = db.query(Role).filter(Role.id == role.id).first()
   if role_delete:
      role_delete.deleted = True
      role_delete.deleted_by = role.user_id
      role_delete.deleted_at = func.now()
      db.commit()
      db.refresh(role_delete)
   return {
      "status": "Success",
      "message": "Role deleted successfully"
   }
