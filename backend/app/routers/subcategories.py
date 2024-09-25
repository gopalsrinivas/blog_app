from fastapi import Query
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.subcategories import Subcategory
from app.schemas.subcategories import SubcategoryModel, SubcategoryCreateModel, SubcategoryUpdateModel
from app.core.database import get_db
from app.services.subcategories import (
    create_subcategory, get_all_subcategories, get_subcategory_by_id, update_subcategory, soft_delete_subcategory, get_subcategories_by_category_id
)
from app.core.logging import logging

router = APIRouter()

@router.post("/", response_model=dict, summary="Create new Subcategories")
async def create_subcategory_route(
    subcategory_data: SubcategoryCreateModel, db: AsyncSession = Depends(get_db)
):
    try:
        existing_subcategories = await db.execute(select(Subcategory.name).where(Subcategory.name.in_(subcategory_data.names)))
        existing_names = existing_subcategories.scalars().all()
        if existing_names:
            raise HTTPException(
                status_code=400,
                detail=f"Subcategory names already exist: {', '.join(existing_names)}"
            )
        new_subcategories = await create_subcategory(db, subcategory_data)
        logging.info(f"{len(new_subcategories)} subcategories created.")
        return {
            "status_code": 201,
            "message": "Subcategories created successfully",
            "data": [SubcategoryModel.from_orm(subcat) for subcat in new_subcategories]
        }

    except HTTPException as he:
        logging.error(f"HTTP error: {he.detail}")
        raise he
    except Exception as e:
        logging.error(f"Failed to create subcategories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create subcategories")


@router.get("/all/", response_model=dict, summary="List of Subcategories")
async def get_subcategories_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    db: AsyncSession = Depends(get_db)
):
    try:
        subcategories, total_count = await get_all_subcategories(db, skip=skip, limit=limit)
        logging.info("Successfully retrieved all categories.")
        return {
            "status_code": 200,
            "message": "Subcategories retrieved successfully",
            "total_count": total_count,
            "data": [SubcategoryModel.from_orm(subcat) for subcat in subcategories]
        }
    except Exception as e:
        logging.error(f"Failed to fetch subcategories: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch subcategories")


@router.get("/{subcategory_id}", response_model=dict, summary="Retrieve a Subcategory by ID")
async def get_subcategory_by_id_route(subcategory_id: int, db: AsyncSession = Depends(get_db)):
    try:
        subcategory = await get_subcategory_by_id(db, subcategory_id)
        print(f"Retrived subcategory: {subcategory}")
        if not subcategory:
            raise HTTPException(
                status_code=404, detail="Subcategory not found")

        logging.info(f"Subcategory retrieved: {subcategory.name}")
        return {
            "status_code": 200,
            "message": "Subcategory retrieved successfully",
            "data": SubcategoryModel.from_orm(subcategory)
        }
    except Exception as e:
        logging.error(f"Failed to fetch subcategory: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch subcategory")


@router.put("/{subcategory_id}", response_model=dict, summary="Update a Subcategory by ID")
async def update_subcategory_route(
    subcategory_id: int, subcategory_data: SubcategoryUpdateModel, db: AsyncSession = Depends(get_db)
):
    try:
        updated_subcategory = await update_subcategory(db, subcategory_id, subcategory_data)
        if not updated_subcategory:
            raise HTTPException(
                status_code=404, detail="Subcategory not found")

        logging.info(f"Subcategory updated: {
                     updated_subcategory.name or 'Unnamed'}")

        return {
            "status_code": 200,
            "message": "Subcategory updated successfully",
            # Convert to response model
            "data": SubcategoryModel.from_orm(updated_subcategory)
        }
    except HTTPException as he:
        logging.error(f"HTTP error: {he.detail}")
        raise he
    except Exception as e:
        logging.error(f"Failed to update subcategory: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to update subcategory")
        
        
@router.delete("/{subcategory_id}", response_model=dict, summary="Delete a Subcategory by ID")
async def delete_subcategory_route(subcategory_id: int, db: AsyncSession = Depends(get_db)):
    try:
        updated_subcategory = await soft_delete_subcategory(db, subcategory_id)
        if not updated_subcategory:
            raise HTTPException(
                status_code=404, detail="Subcategory not found")

        logging.info(f"Subcategory soft deleted with ID: {subcategory_id}")
        return {
            "status_code": 200,
            "message": "Subcategory soft deleted successfully",
            "data": {"id": updated_subcategory.id, "is_active": updated_subcategory.is_active}
        }

    except Exception as e:
        logging.error(f"Failed to soft delete subcategory: {
                      str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to soft delete subcategory")


@router.get("/categories/{category_id}/subcategories", response_model=dict)
async def get_subcategories_for_category(
    category_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Fetch subcategories
        result = await get_subcategories_by_category_id(db, category_id, skip, limit)

        # Check if subcategories were found
        if not result["subcategories"]:
            logging.warning(
                f"No subcategories found for category ID {category_id}.")
            raise HTTPException(
                status_code=404, detail="No subcategories found for this category."
            )

        # Return the response with the category details and subcategories
        return {
            "status_code": 200,
            "message":"Subcategory retrieved successfully",
            "category_id": result["category_id"],
            "cat_id": result["cat_id"],
            "category_name": result["category_name"],
            "total_records": result["total_records"],
            "data": [
                {
                    "id": sub.id,
                    "name": sub.name,
                    "subcat_id": sub.subcat_id,
                    "is_active": sub.is_active
                }
                for sub in result["subcategories"]
            ]
        }

    except HTTPException as e:
        logging.error(f"HTTPException: {
                      e.detail} (Category ID: {category_id})")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in fetching subcategories for category ID {
                      category_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to fetch subcategories for the category.")
