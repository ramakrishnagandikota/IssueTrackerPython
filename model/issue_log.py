from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Date, ForeignKey, Table, Text
from sqlalchemy.sql import func
import uuid
from db.config import Base
from sqlalchemy.orm import relationship

class IssueLog(Base):

    __tablename__ = "issues_log"

    id= Column(UNIQUEIDENTIFIER, primary_key =True, default=uuid.uuid4, unique = True)
    log_name = Column(Text, nullable = False)
    issues_id = Column(UNIQUEIDENTIFIER, ForeignKey("issues.id"), nullable=True)
    created_at = Column(DateTime, default = func.now())
    updated_at = Column(DateTime, default= func.now(), onupdate= func.now())
    created_by = Column(String(255), nullable = True)
    updated_by = Column(String(255), nullable = True)
    deleted = Column(Boolean, nullable=False, default=False)
    deleted_by = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable = True)
    deleted_at = Column(DateTime, nullable= True)
    
    issue = relationship("Issue", back_populates="issues_log")