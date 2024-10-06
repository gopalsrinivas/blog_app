from typing import List, Dict, Any, Optional,Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy import func, desc
from app.models.categories import Category
from app.schemas.categories import CategoryCreateModel, CategoryModel, CategoryUpdateModel
from app.core.logging import logging
from datetime import datetime

async def generate_cat_id(db: AsyncSession) -> str:
    try:
        # Get the last inserted ID
        result = await db.execute(select(func.max(Category.id)))
        max_id = result.scalar_one_or_none()
        # Start from 1 if no categories exist
        new_id = (max_id + 1) if max_id is not None else 1
        return f"cat_{new_id}"
    except Exception as e:
        logging.error(f"Error generating category ID: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating category ID")

async def create_category(db: AsyncSession, category_data: CategoryCreateModel):
    try:
        categories = []
        for name in category_data.names:
            new_cat_id = await generate_cat_id(db)
            new_category = Category(
                cat_id=new_cat_id,
                name=name,
                is_active=category_data.is_active,
            )
            db.add(new_category)
            categories.append(new_category)

        await db.commit()
        for category in categories:
            await db.refresh(category)
        logging.info(f"Successfully created {len(categories)} categories.")
        return categories
    except Exception as e:
        logging.error(f"Failed to create categories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create categories")

async def get_all_categories(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.id.desc())
            .offset(skip)
            .limit(limit)
        )
        categories = result.scalars().all()
        # Get the total count of active categories
        total_count_result = await db.execute(select(func.count(Category.id)).where(Category.is_active == True))
        total_count = total_count_result.scalar()
        logging.info("Successfully retrieved all active categories.")
        return categories, total_count
    except Exception as e:
        logging.error(f"Failed to fetch categories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch categories")


async def get_category_by_id(db: AsyncSession, category_id: int):
    try:
        category = await db.get(Category, category_id)
        if not category:
            logging.warning(f"Category with ID {category_id} not found.")
            return None
        logging.info(f"Category found: {category.name}")
        return category
    except Exception as e:
        logging.error(f"Error retrieving category by ID {category_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving category")


async def update_category(db: AsyncSession, category_id: int, category_data: CategoryUpdateModel):
    try:
        category = await get_category_by_id(db, category_id)
        if not category:
            logging.warning(f"Category with ID {category_id} not found.")
            return None
        # Update fields if they are provided
        if category_data.name is not None:
            category.name = category_data.name
        if category_data.is_active is not None:
            category.is_active = category_data.is_active
        # Commit changes to the database
        await db.commit()
        await db.refresh(category)
        logging.info(f"Category with ID {category_id} updated successfully.")
        return category
    except Exception as e:
        logging.error(f"Failed to update category with ID {category_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update category")


async def soft_delete_category(db: AsyncSession, category_id: int):
    try:
        category = await get_category_by_id(db, category_id)
        if not category:
            logging.warning(f"Category with ID {category_id} not found for soft delete.")
            return None
        # Set is_active to False for soft delete
        category.is_active = False
        await db.commit()
        await db.refresh(category)
        logging.info(f"Category with ID {category_id} soft deleted successfully.")
        return category
    except Exception as e:
        logging.error(f"Failed to soft delete category with ID {category_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to soft delete category")


async def get_category_by_search(
    db: AsyncSession,
    category_id: Optional[int] = None,
    name: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Tuple[List[Category], int]:
    try:
        # Build the query dynamically based on the provided parameters
        query = select(Category)

        # Add filters based on provided search parameters
        if category_id:
            query = query.where(Category.id == category_id)
        if name:
            query = query.where(Category.name.ilike(f"%{name}%"))
        if is_active is not None:
            query = query.where(Category.is_active == is_active)

        # Execute the query for categories
        result = await db.execute(query)
        # Fetch all matching categories
        categories = result.scalars().all()

        # Execute a count query to get the total number of matching records
        total_count = await db.execute(select(func.count()).select_from(Category).where(
            (Category.id == category_id) if category_id else True,
            (Category.name.ilike(f"%{name}%")) if name else True,
            (Category.is_active == is_active) if is_active is not None else True
        ))
        total_count_value = total_count.scalar()
        logging.info(f"Total categories found: {total_count_value}")
        return categories, total_count_value
    except Exception as e:
        logging.error(f"Error retrieving categories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving categories")

