from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.categories import CategoryCreateModel
from app.services.categories import CategoryService
from app.core.database import get_db
from app.core.logging import logger

router = APIRouter()


@router.post("/")
async def create_category(category_data: CategoryCreateModel, db: AsyncSession = Depends(get_db)):
    # Call service method and get the response
    response = await CategoryService.create_category(db=db, category_data=category_data)
    # Return the response directly (with the custom structure)
    return response
