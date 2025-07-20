from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import UUID, Boolean, Column, DateTime, Integer, String, Date, ForeignKey, Table, Text
from sqlalchemy.sql import func
import uuid
from db.config import Base
from sqlalchemy.orm import relationship

class IssueAttachments(Base):

    __tablename__ = "issues_attachments"

    id= Column(UNIQUEIDENTIFIER, primary_key =True, default=uuid.uuid4, unique = True)
    #issues_id = Column(String(100), ForeignKey("issues.id"), nullable = False)
    issues_id = Column(UNIQUEIDENTIFIER, ForeignKey("issues.id"), nullable=False)
    file_name = Column(String(100), nullable = False)
    ext = Column(String(100), nullable = True)
    size = Column(String(100), nullable = True)
    path = Column(Text, nullable = False)
    created_at = Column(DateTime, default = func.now())
    updated_at = Column(DateTime, default= func.now(), onupdate= func.now())

    created_by = Column(String(255), nullable = True)
    updated_by = Column(String(255), nullable = True)
    deleted = Column(Boolean, nullable=False, default=False)
    deleted_by = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable = True)
    deleted_at = Column(DateTime, nullable= True)
    
    issue = relationship("Issue", back_populates="attachments")