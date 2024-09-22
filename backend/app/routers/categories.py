from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.categories import CategoryModel, CategoryCreateModel, CategoryUpdateModel
from app.services.categories import CategoryService
from app.core.database import get_db
from app.core.logging import logger
from typing import Dict, Any, Optional

router = APIRouter()


@router.post("/create-or-bulk/")
async def create_category(category_data: CategoryCreateModel, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.create_categories(db=db, names=category_data.names, is_active=category_data.is_active)
    if any(resp["status_code"] != 201 for resp in response):
        logger.error("Failed to create one or more categories.")
        raise HTTPException(
            status_code=400, detail="One or more categories could not be created.")
    logger.info("Categories created successfully.")
    return response


@router.get("/", response_model=Dict[str, Any])
async def get_categories(cat_id: Optional[str] = None, name: Optional[str] = None, is_active: Optional[bool] = None, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.get_categories(db=db, cat_id=cat_id, name=name, is_active=is_active, skip=skip, limit=limit)

    if response["status"] == "success":
        logger.info("Successfully retrieved categories.")
        return response
    else:
        logger.error(f"Failed to retrieve categories: {response['message']}")
        raise HTTPException(status_code=500, detail=response["message"])


@router.get("/all/", response_model=Dict[str, Any])
async def get_all_categories(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.get_all_categories(db=db, skip=skip, limit=limit)

    if response["status"] == "success":
        logger.info("Successfully retrieved all categories.")
        return response
    else:
        logger.error(f"Failed to retrieve all categories: {
                     response['message']}")
        raise HTTPException(status_code=500, detail=response["message"])


@router.get("/{category_id}", response_model=Dict[str, Any])
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.get_category_by_id(db=db, category_id=category_id)

    if response["status"] == "success":
        return response
    else:
        logger.error(f"Failed to retrieve category with ID {
                     category_id}: {response['message']}")
        raise HTTPException(status_code=404, detail=response["message"])


@router.put("/{category_id}", response_model=Dict[str, Any])
async def update_category(category_id: int, category_data: CategoryUpdateModel, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.update_category(db=db, category_id=category_id, category_data=category_data)

    if response["status"] == "success":
        logger.info(f"Category with ID {category_id} updated successfully.")
        return response
    else:
        logger.error(f"Failed to update category with ID {
                     category_id}: {response['message']}")
        raise HTTPException(status_code=400, detail=response["message"])


@router.delete("/soft-delete/{category_id}", response_model=Dict[str, Any])
async def soft_delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    response = await CategoryService.soft_delete_category(db=db, category_id=category_id)

    if response["status"] == "success":
        logger.info(f"Category with ID {
                    category_id} soft deleted successfully.")
        return response
    else:
        logger.error(f"Failed to soft delete category with ID {
                     category_id}: {response['message']}")
        raise HTTPException(status_code=404, detail=response["message"])
