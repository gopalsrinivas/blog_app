from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class SubcategoryModel(BaseModel):
    id: int
    category_id: int
    subcat_id: str
    name: str
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "Sample Category",
                "is_active": True
            }
        }


class SubcategoryCreateModel(BaseModel):
    category_id: int
    names: List[str]
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "category_id": 1,
                "names": ["Sample Subcategory 1", "Sample Subcategory 2"],
                "is_active": True
            }
        }

class SubcategoryUpdateModel(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
