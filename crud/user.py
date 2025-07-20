from operator import or_
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from schema.user import UserCreate, UserUpdate, UserDelete,UserSearch
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from model.user import User, UserRole
from model.role import Role
import uuid
from fastapi import HTTPException
from passlib.context import CryptContext

ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
ALGORITHM = "HS256"
password_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def read_users(db : Session, skip: int = 0,limit: int = 10):
   try:
      userData = db.query(User).order_by(User.created_at).filter(User.deleted == False).offset(skip).limit(limit).all()
      return [
         {
         "id" : user.id,
         "first_name" : user.first_name,
         "last_name" : user.last_name,
         "email" : user.email,
         "mobile_number" : user.mobile_number,
         "address" : user.address,
         "date_of_birth" : user.date_of_birth,
         "status" : user.status,
         "profile_picture" : user.profile_picture,
         "created_at" : user.created_at,
         "updated_at" : user.updated_at,
         "role" : [role.role_name
            for role in db.query(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .join(User, UserRole.user_id == User.id)
            .filter(User.id == user.id)
            .all()]
         } for user in userData
      ]
   except Exception as e:
      print({str(e)})
      raise HTTPException(status_code=500, detail= str(e))
   
   
def read_user_id(db : Session, user_id : str):
   try:
      user = db.query(User).filter(User.id == user_id).first()
      return {
         "id" : user.id,
         "first_name" : user.first_name,
         "last_name" : user.last_name,
         "email" : user.email,
         "mobile_number" : user.mobile_number,
         "address" : user.address,
         "date_of_birth" : user.date_of_birth,
         "status" : user.status,
         "profile_picture" : user.profile_picture,
         "created_at" : user.created_at,
         "updated_at" : user.updated_at,
         "role" : db.query(Role.id,Role.role_name).join(UserRole,UserRole.role_id == Role.id).join(User,UserRole.user_id == User.id).filter(User.id == user.id).all()
      }
   except Exception as e:
      print({str(e)})
      raise HTTPException(status_code=500, detail= str(e))
   

def post_user(db: Session, user: UserCreate):
   try:
      checkUser = checkUser = db.query(User).filter(
               or_(
                  func.lower(User.email) == user.email.lower(),
                  User.mobile_number == user.mobile_number
               )
            ).first()
      if checkUser:
         return {
            "status": "Fail",
            "message": "User with this Email / Mobile number is already created."
         }
         
      hashed_password = password_context.hash(user.password)
      userCreate = User(id = uuid.uuid4(), password = hashed_password, email = user.email.lower(), **user.dict(exclude={'password','role_id','email'}))
      db.add(userCreate)
      db.commit()
      db.refresh(userCreate)
      
      userRole = UserRole(id = uuid.uuid4(), user_id = userCreate.id, role_id = user.role_id)
      db.add(userRole)
      db.commit()
      db.refresh(userRole)
      
      return {
         "status" : "Success",
         "message" : "User created successfully"
      }
      
   except Exception as e:
      print({str(e)})
      raise HTTPException(status_code=500, detail= str(e))
   
# def update_user_id(user: UserCreate, db: Session):
   try:
      checkUser = db.query(User).filter(User.id == user.id).first()
      
      if checkUser:
         for key,value in user.dict(exclude={'role_id'}).items():
            setattr(checkUser,key,value)
         db.commit()
         db.refresh(checkUser)
         
         checkRole = db.query(UserRole).filter(UserRole.user_id == checkUser.id).first()
         if checkRole:
            #if the role_id in user_roles table is not matching with role_id from payload(swagger)
            if checkRole.role_id != user.role_id:
               db.delete(checkRole)
               db.commit()
               
               userRole = UserRole(id = uuid.uuid4(), user_id = checkUser.id, role_id = user.role_id)
               db.add(userRole)
               db.commit()
               db.refresh(userRole)
               
         else:
            userRole = UserRole(id = uuid.uuid4(), user_id = checkUser.id, role_id = user.role_id)
            db.add(userRole)
            db.commit()
            db.refresh(userRole)
            
         return{
            "status" : "Success",
            "message" : "User updated successfully."
         }
            
      else:
         return {
            "status" : "fail",
            "message" : "There is no user with given information."
         }
   
   except Exception as e:
      print({str(e)})
      raise HTTPException(status_code=500, detail= str(e))
   
def update_user_id(user: UserCreate, db: Session):
    try:
        checkUser = db.query(User).filter(User.id == user.id).first()

        if not checkUser:
            return {
                "status": "fail",
                "message": "There is no user with given information."
            }

        # ✅ Check if email or mobile number exists for another user
      #   existing = db.query(User).filter(
      #       or_(
      #           func.lower(User.email) == user.email.lower(),
      #           User.mobile_number == user.mobile_number
      #       ),
      #       User.id != user.id  # exclude current user
      #    ).first()
      
        existing = db.query(User).filter(
               or_(
                  func.lower(User.email) == user.email.lower(),
                  User.mobile_number == user.mobile_number
               ),
               User.id != user.id,  # this line ensures current user is excluded
               User.deleted == False
            ).first()

        if existing:
            return {
               "status": "Fail",
               "message": "User with this Email or Mobile number already exists."
            }


        # ✅ Update user fields except role_id
        for key, value in user.dict(exclude={'role_id'}).items():
            setattr(checkUser, key, value)
        db.commit()
        db.refresh(checkUser)

        # ✅ Update role
        checkRole = db.query(UserRole).filter(UserRole.user_id == checkUser.id).first()
        if checkRole:
            if checkRole.role_id != user.role_id:
                db.delete(checkRole)
                db.commit()
                userRole = UserRole(id=uuid.uuid4(), user_id=checkUser.id, role_id=user.role_id)
                db.add(userRole)
                db.commit()
                db.refresh(userRole)
        else:
            userRole = UserRole(id=uuid.uuid4(), user_id=checkUser.id, role_id=user.role_id)
            db.add(userRole)
            db.commit()
            db.refresh(userRole)

        return {
            "status": "Success",
            "message": "User updated successfully."
        }

    except Exception as e:
        print({str(e)})
        raise HTTPException(status_code=500, detail=str(e))
     
     
def userSearch(search: UserSearch, db: Session,skip: int = 0,limit: int = 10):
   result = (
        db.query(User)
        .filter(or_(
            User.first_name.ilike(f"%{search.search}%"),
            User.last_name.ilike(f"%{search.search}%"),
            User.email.ilike(f"%{search.search}%")
        ))
        .order_by(User.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Convert result into JSON serializable format
   users_list = []
   for user in result:
      user_dict = {
         "id": user.id,
         "first_name" : user.first_name,
         "last_name" : user.last_name,
         "email": user.email,
         "mobile_number": user.mobile_number,
         "address": user.address,
         "date_of_birth": user.date_of_birth,  # Ensure datetime is serializable
         "status": user.status,
         "profile_picture": user.profile_picture,
         "created_at": user.created_at.isoformat() if user.created_at else None,
         "updated_at": user.updated_at.isoformat() if user.updated_at else None,
         "role": [
               {"id": role.id, "role_name": role.role_name}
               for role in db.query(Role.id, Role.role_name)
               .join(UserRole, UserRole.role_id == Role.id)
               .join(User, UserRole.user_id == User.id)
               .filter(User.id == user.id)
               .all()
         ]
      }
      users_list.append(user_dict)

   return jsonable_encoder(users_list) 

def delete_user_id(user: UserDelete, db: Session):
   checkUser = db.query(User).filter(User.id == user.id).first()
   if checkUser:
      checkUser.deleted = True
      checkUser.deleted_at = func.now()
      checkUser.deleted_by = user.user_id
      db.commit()
      db.refresh(checkUser)
      return {
         "status" : "Success",
         "message" : "User deleted successfully"
      }
   else:
        return None