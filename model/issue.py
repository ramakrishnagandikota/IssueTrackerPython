from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Date, ForeignKey, Table, Text
from sqlalchemy.sql import func
import uuid
from db.config import Base
from sqlalchemy.orm import relationship

class Issue(Base):

    __tablename__ = "issues"

    id= Column(UNIQUEIDENTIFIER, primary_key =True, default=uuid.uuid4, unique = True)
    title = Column(String(250), nullable = False)
    description = Column(Text, nullable = False)
    type= Column(UNIQUEIDENTIFIER, ForeignKey("type.id"), nullable = False)
    state= Column(UNIQUEIDENTIFIER, ForeignKey("state.id"), nullable = False)
    priority= Column(UNIQUEIDENTIFIER, ForeignKey("priority.id"), nullable = False)
    azure_ticket_no= Column(String(100), nullable = False)
    status = Column(Integer, nullable = True, default=None)
    created_at = Column(DateTime, default = func.now())
    updated_at = Column(DateTime, default= func.now(), onupdate= func.now())
    created_by = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable = True)
    updated_by = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable = True)
    deleted = Column(Boolean, nullable=False, default=False)
    deleted_by = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable = True)
    deleted_at = Column(DateTime, nullable= True)
    
    attachments = relationship("IssueAttachments", back_populates="issue", lazy="joined")
    state_history = relationship("IssueStateHistory", back_populates="issue", lazy="joined")
    issues_log = relationship("IssueLog", back_populates="issue", lazy="joined")