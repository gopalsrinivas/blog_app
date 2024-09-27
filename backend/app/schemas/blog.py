from fastapi import UploadFile
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BlogCreateModel(BaseModel):
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    title: str
    content: str
    is_active: Optional[bool] = True


class BlogUpdateModel(BaseModel):
    id: int
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    blog_id: str
    title: str
    content: str
    is_active: bool


class BlogResponseModel(BaseModel):
    id: int
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    blog_id: str
    title: str
    content: str
    image: Optional[str]
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True
