from sqlalchemy.orm import Session
from app import models, schemas

def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(
        from_number=message.from_number,
        message=message.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, limit: int = 100):
    return db.query(models.Message).order_by(models.Message.created_at.desc()).limit(limit).all()
