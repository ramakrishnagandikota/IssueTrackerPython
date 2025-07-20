from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Date
from sqlalchemy.sql import func
import uuid
from db.config import Base
from sqlalchemy.orm import relationship

class Permission(Base):

    __tablename__ = "permissions"

    id= Column(UNIQUEIDENTIFIER, primary_key =True, default=uuid.uuid4, unique = True)
    permission_name = Column(String(50), nullable = False)
    description= Column(String(50), nullable = False)
    status = Column(Integer, nullable = False, default=1)
    created_at = Column(DateTime, default = func.now())
    updated_at = Column(DateTime, default= func.now(), onupdate= func.now())

    created_by = Column(String(255), nullable = True)
    updated_by = Column(String(255), nullable = True)
    deleted = Column(Boolean, nullable=False, default=False)
    deleted_by = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable = True)
    deleted_at = Column(DateTime, nullable= True)
    
    # user = relationship("User", backref = "role")
    
    roles_permissions = relationship("RolePermission", back_populates="permission")
    roles = relationship("Role", secondary="roles_permissions", viewonly=True, back_populates="permissions")