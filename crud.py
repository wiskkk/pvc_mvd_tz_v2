from sqlalchemy.orm import Session

import models
import schemas


def create_image_comment(db: Session, image_comment: schemas.ImageCommentIn):
    db_image_comment = models.ImageComment(**image_comment.dict())
    db.add(db_image_comment)
    db.commit()
    db.refresh(db_image_comment)
    return db_image_comment


def get_image_comments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ImageComment).offset(skip).limit(limit).all()


def get_image_comment(db: Session, image_comment_id: int):
    return db.query(models.ImageComment).filter(models.ImageComment.id == image_comment_id).first()


def update_image_comment(db: Session, image_comment_id: int, image_comment: schemas.ImageCommentIn):
    db_image_comment = db.query(models.ImageComment).filter(models.ImageComment.id == image_comment_id).first()
    if db_image_comment:
        for field, value in image_comment.dict(exclude_unset=True).items():
            setattr(db_image_comment, field, value)
        db.commit()
        db.refresh(db_image_comment)
        return db_image_comment


def delete_image_comment(db: Session, image_comment_id: int):
    db_image_comment = db.query(models.ImageComment).filter(models.ImageComment.id == image_comment_id).first()
    if db_image_comment:
        db.delete(db_image_comment)
        db.commit()
        return {"message": "Image comment deleted successfully"}
