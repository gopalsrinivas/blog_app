from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class CategoryModel(BaseModel):
    id: int
    cat_id: str
    name: str
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "Sample Category",
                "is_active": True
            }
        }


class CategoryCreateModel(BaseModel):
    names: List[str]  # List for bulk insert
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "names": ["Sample Category 1", "Sample Category 2"],
                "is_active": True
            }
        }


class CategoryUpdateModel(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
