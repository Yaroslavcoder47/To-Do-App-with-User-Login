from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from typing import List, Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Operations with users
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def vertify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db=db, email=email)
    if not user:
        return None
    if not vertify_password(password, user.hashed_password):
        return None
    return user

# Operations with tasks
def create_task(db: Session, owner_id: int, task: schemas.TaskCreate) -> Optional[models.Task]:
    db_task = models.Task(title=task.title, description=task.description, owener_id=owner_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, owner_id: int) -> List[models.Task]:
    return db.query(models.Task).filter(models.Task.owner_id == owner_id).all()

def get_task(db: Session, owner_id: int, task_id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.owner_id == owner_id,
                                        models.Task.task_id == task_id).first()

def update_task(db: Session, db_task: models.Task, updates: schemas.TaskUpdate) -> models.Task:
    if updates.title is not None:
        db_task.title = updates.title
    if updates.description is not None:
        db_task.description = updates.description
    if updates.completed is not None:
        db_task.completed = updates.completed
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, db_task: models.Task):
    db.delete(db_task)
    db.commit()
    