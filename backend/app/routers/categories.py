from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.categories import CategoryModel,CategoryCreateModel,CategoryUpdateModel
from app.services.categories import CategoryService
from app.core.database import get_db
from app.core.logging import logger

router = APIRouter()


@router.post("/create-or-bulk/")
async def create_category(category_data: CategoryCreateModel, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.create_categories(db=db, names=category_data.names, is_active=category_data.is_active)
    return response


@router.get("/all", response_model=Dict[str, Any])
async def get_all_categories(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.get_all_categories(db=db, skip=skip, limit=limit)
    if response["status"] == "success":
        logger.info(f"Successfully retrieved {len(response['data'])} categories.")
        return response
    else:
        logger.error(f"Failed to retrieve categories: {response['message']}")
        raise HTTPException(status_code=500, detail=response["message"])


@router.get("/{category_id}", response_model=Dict[str, Any])
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.get_category_by_id(db=db, category_id=category_id)
    if response["status"] == "success":
        logger.info(f"Successfully retrieved category with id {category_id}.")
        return response
    else:
        logger.error(f"Failed to retrieve category: {response['message']}")
        raise HTTPException(status_code=404, detail=response["message"])


@router.put("/{category_id}", response_model=Dict[str, Any])
async def update_category(category_id: int, category_data: CategoryUpdateModel, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.update_category(db=db, category_id=category_id, category_data=category_data)
    if response["status"] == "success":
        logger.info(f"Successfully updated category with id {category_id}.")
        return response
    else:
        logger.error(f"Failed to update category: {response['message']}")
        raise HTTPException(status_code=404, detail=response["message"])
