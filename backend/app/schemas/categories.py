from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CategoryModel(BaseModel):
    id: int
    cat_id: str
    name: str
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "cat_id": "cat__001",
                "name": "Sample Category",
                "is_active": True
            }
        }


class CategoryCreateModel(BaseModel):
    name: str
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sample Category",
                "is_active": True
            }
        }


class CategoryUpdateModel(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
