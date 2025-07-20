from fastapi import Depends
from sqlalchemy.orm import Session
from db.config import SessionLocal
from model.role import Role
from router.auth import require_role  # adjust based on your project structure

def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
        
def get_all_roles_dependency(db: Session = Depends(get_db)):
    all_roles = db.query(Role.role_name).all()
    role_names = [r.role_name for r in all_roles]
    return require_role(role_names)
