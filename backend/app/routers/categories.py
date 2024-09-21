from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.categories import *
from app.services.categories import CategoryService
from app.core.database import get_db

router = APIRouter()


@router.post("/create-or-bulk/")
async def create_category(category_data: CategoryCreateModel, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.create_categories(db=db, names=category_data.names, is_active=category_data.is_active)
    return response
