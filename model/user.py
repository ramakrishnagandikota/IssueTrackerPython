from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from db.config import Base


class User(Base):

    __tablename__ = "users"

    id= Column(UNIQUEIDENTIFIER, primary_key =True, default=uuid.uuid4, unique = True)
    first_name = Column(String(50), nullable = False)
    last_name = Column(String(50), nullable = False)
    email= Column(String(50), nullable = False)
    mobile_number  = Column(String(50), nullable = False)
    password = Column(String(255), nullable = False)
    address = Column(String(50), nullable = True)
    date_of_birth = Column(String(50), nullable = True)
    status = Column(Integer, nullable = False, default=1)
    profile_picture = Column(String(255), nullable = True)
    created_at = Column(DateTime, default = func.now())
    updated_at = Column(DateTime, default= func.now(), onupdate= func.now())
    created_by = Column(String(255), nullable = True)
    updated_by = Column(String(255), nullable = True)
    deleted = Column(Boolean, nullable=False, default=False)
    deleted_by = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable = True)
    deleted_at = Column(DateTime, nullable= True)
    
class UserRole(Base):
    
    __tablename__ = "users_roles"
    
    id= Column(UNIQUEIDENTIFIER, primary_key =True, default=uuid.uuid4, unique = True)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"),nullable = False)
    role_id = Column(UNIQUEIDENTIFIER,ForeignKey("roles.id"),nullable = False)
    created_at = Column(DateTime, default = func.now())
    updated_at = Column(DateTime, default= func.now(), onupdate= func.now())
    
    
    role = relationship("Role", backref= "users_roles")