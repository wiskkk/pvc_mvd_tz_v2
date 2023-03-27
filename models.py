from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    contents = Column(LargeBinary)
    comments = relationship("ImageComment", back_populates="image")


class ImageComment(Base):
    __tablename__ = "image_comments"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String)
    image_id = Column(Integer, ForeignKey("images.id"))

    image = relationship("Image", back_populates="comments")