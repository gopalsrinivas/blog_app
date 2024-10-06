from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from app.schemas.categories import CategoryModel, CategoryCreateModel, CategoryUpdateModel
from app.services.categories import *
from app.core.database import get_db
from app.core.logging import logger
from typing import Dict, Any, Optional

router = APIRouter()

@router.post("/", response_model=dict, summary="Create new Categories")
async def create_category_route(
    category_data: CategoryCreateModel, db: AsyncSession = Depends(get_db)
):
    try:
        existing_categories = await db.execute(select(Category.name).where(Category.name.in_(category_data.names)))
        existing_names = existing_categories.scalars().all()
        if existing_names:
            raise HTTPException(
                status_code=400,
                detail=f"Category names already exist: {', '.join(existing_names)}"
            )
        new_categories = await create_category(db, category_data)
        logging.info(f"{len(new_categories)} categories created.")
        return {
            "status_code": 201,
            "message": "Categories created successfully",
            "data": [CategoryModel.from_orm(cat) for cat in new_categories]
        }
    except HTTPException as he:
        logging.error(f"HTTP error: {he.detail}")
        raise he
    except Exception as e:
        logging.error(f"Failed to create categories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create categories")

@router.get("/all/", response_model=dict, summary="List of categories")
async def get_categories_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    db: AsyncSession = Depends(get_db)
):
    try:
        categories, total_count = await get_all_categories(db, skip=skip, limit=limit)
        logging.info("Successfully retrieved all categories.")

        return {
            "status_code": 200,
            "message": "Categories retrieved successfully",
            "total_count": total_count,
            "data": [CategoryModel.from_orm(cat) for cat in categories]
        }
    except Exception as e:
        logging.error(f"Failed to fetch categories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch categories")


@router.get("/{category_id}", response_model=dict, summary="Retrieve a Category by ID")
async def get_category_by_id_route(category_id: int, db: AsyncSession = Depends(get_db)):
    try:
        category = await get_category_by_id(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        logging.info(f"Category retrieved: {category.name}")
        return {
            "status_code": 200,
            "message": "Category retrieved successfully",
            "data": CategoryModel.from_orm(category)
        }
    except HTTPException as he:
        logging.error(f"HTTP error: {he.detail}", exc_info=True)
        raise he  # Re-raise HTTPException to avoid logging it twice
    except Exception as e:
        logging.error(f"Failed to fetch category: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch category")


@router.put("/{category_id}", response_model=dict, summary="Update a Category by ID")
async def update_category_route(
    category_id: int, category_data: CategoryUpdateModel, db: AsyncSession = Depends(get_db)
):
    try:
        updated_category = await update_category(db, category_id, category_data)
        if not updated_category:
            raise HTTPException(status_code=404, detail="Category not found")

        logging.info(f"Category updated: {updated_category.name or 'Unnamed'}")

        return {
            "status_code": 200,
            "message": "Category updated successfully",
            "data": CategoryModel.from_orm(updated_category)
        }

    except HTTPException as he:
        logging.error(f"HTTP error: {he.detail}", exc_info=True)
        raise he 

    except Exception as e:
        logging.error(f"Failed to update category: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update category")


@router.delete("/{category_id}", response_model=dict, summary="Delete a category by ID")
async def delete_category_route(category_id: int, db: AsyncSession = Depends(get_db)):
    try:
        delete_category = await soft_delete_category(db, category_id)
        if not delete_category:
            raise HTTPException(status_code=404, detail="Category not found")

        logging.info(f"Category soft deleted with ID: {category_id}")
        return {
            "status_code": 200,
            "message": "Category soft deleted successfully",
            "data": {"id": delete_category.id, "is_active": delete_category.is_active}
        }

    except HTTPException as he:
        logging.error(f"HTTP error during deletion: {he.detail}")
        raise he

    except Exception as e:
        logging.error(f"Failed to soft delete category: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to soft delete category")


@router.get("/search/", response_model=Dict[str, Any], summary="Search for Categories")
async def search_category(
    category_id: Optional[int] = None,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get all matching categories and the total count
        categories, total_count = await get_category_by_search(
            db, category_id=category_id, name=name, is_active=is_active
        )

        # Check if there are no matching categories
        if not categories:
            raise HTTPException(status_code=404, detail="Category not found")

        # Return all categories and total count
        return {
            "status_code": 200,
            "message": "Categories retrieved successfully",
            "total_count": total_count,
            # Convert each category to the response model
            "data": [CategoryModel.from_orm(category) for category in categories]
        }

    except HTTPException as he:
        logging.error(f"HTTP error: {he.detail}")
        raise he
    except Exception as e:
        logging.error(f"Failed to search categories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to search categories")
