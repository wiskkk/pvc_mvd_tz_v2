from pydantic import BaseModel


class Image(BaseModel):
    id: int
    filename: str

    # contents: bytes

    class Config:
        orm_mode = True


class ImageCommentIn(BaseModel):
    comment: str
    image_id: int


class ImageCommentOut(BaseModel):
    id: int
    comment: str
    image_id: int

    class Config:
        orm_mode = True
