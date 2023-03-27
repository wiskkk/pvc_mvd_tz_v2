import io
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import text, func
from sqlalchemy.orm import Session

import crud
import schemas
from db import SessionLocal, engine, Base
from models import Image, ImageComment

app = FastAPI()

Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/images/")
async def create_image(image: UploadFile = File(...)):
    contents = await image.read()
    db = SessionLocal()
    query = text("INSERT INTO images (filename, contents) VALUES (:filename, :contents)")
    db.execute(query, {"filename": image.filename, "contents": contents})
    db.commit()
    return {"filename": image.filename}


@app.get("/images", response_model=List[schemas.Image])
async def get_all_images():
    db = SessionLocal()
    image_list = db.query(Image).all()
    db.close()
    return image_list


@app.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: int):
    db = SessionLocal()
    image = db.query(Image).get(image_id)
    if image:
        db.delete(image)
        db.commit()
        db.close()
    else:
        raise HTTPException(status_code=404, detail=f"url item with id {id} not found")

    return None


@app.get("/images/{image_id}")
async def get_image(image_id: int):
    db = SessionLocal()
    image_bytes = db.query(Image).get(image_id).contents
    db.close()

    if not image_bytes:
        raise HTTPException(status_code=404, detail=f"image with id {id} not found")
    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")


@app.post("/image_comments/", response_model=schemas.ImageCommentOut)
def create_image_comment(image_comment: schemas.ImageCommentIn, db: Session = Depends(get_db)):
    return crud.create_image_comment(db=db, image_comment=image_comment)


@app.get("/image_comments/", response_model=List[schemas.ImageCommentOut])
def read_image_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    image_comments = crud.get_image_comments(db=db, skip=skip, limit=limit)
    return image_comments


@app.get("/image_comments/{image_comment_id}", response_model=schemas.ImageCommentOut)
def read_image_comment(image_comment_id: int, db: Session = Depends(get_db)):
    db_image_comment = crud.get_image_comment(db=db, image_comment_id=image_comment_id)
    if db_image_comment is None:
        raise HTTPException(status_code=404, detail="Image comment not found")
    return db_image_comment


@app.put("/image_comments/{image_comment_id}", response_model=schemas.ImageCommentOut)
def update_image_comment(image_comment_id: int, image_comment: schemas.ImageCommentIn, db: Session = Depends(get_db)):
    updated_image_comment = crud.update_image_comment(db=db, image_comment_id=image_comment_id,
                                                      image_comment=image_comment)
    if updated_image_comment is None:
        raise HTTPException(status_code=404, detail="Image comment not found")
    return updated_image_comment


@app.delete("/image_comments/{image_comment_id}")
def delete_image_comment(image_comment_id: int, db: Session = Depends(get_db)):
    deleted_image_comment = crud.delete_image_comment(db=db, image_comment_id=image_comment_id)
    if deleted_image_comment is None:
        raise HTTPException(status_code=404, detail="Image comment not found")
    return {"message": "Image comment deleted successfully"}


@app.get("/stat")
def get_stats(db: Session = Depends(get_db)):
    total_images = db.query(func.count(Image.id)).scalar()
    unique_images = db.query(func.count(Image.id.distinct())).scalar()
    occupied_size_mb = db.query(func.sum(func.length(Image.contents))).scalar() / (1024 * 1024)
    total_comments = db.query(func.count(ImageComment.id)).scalar()
    unique_comments = db.query(func.count(ImageComment.id.distinct())).scalar()
    return {
        "total_images": total_images,
        "unique_images": unique_images,
        "occupied_size_mb": occupied_size_mb,
        "total_comments": total_comments,
        "unique_comments": unique_comments,
    }
