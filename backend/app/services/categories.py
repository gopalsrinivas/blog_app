from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
from app.models.categories import Category
from app.schemas.categories import CategoryCreateModel, CategoryModel, CategoryUpdateModel
from app.core.logging import logger
from sqlalchemy import func, select, desc
from datetime import datetime

def generate_cat_id(category_count: int) -> str:
    return f"cat__{str(category_count + 1).zfill(3)}"
      
class CategoryService:

    @staticmethod
    async def create_categories(db: AsyncSession, names: list, is_active: bool) -> list:
        responses = []

        for name in names:
            try:
                existing_category = await db.execute(
                    select(Category).where(Category.name == name)
                )
                if existing_category.scalars().first():
                    responses.append({
                        "status_code": 400,
                        "status": f"Category '{name}' already exists.",
                        "data": None
                    })
                    continue

                result = await db.execute(select(Category))
                category_count = len(result.scalars().all())

                new_category = Category(
                    cat_id=generate_cat_id(category_count),
                    name=name,
                    is_active=is_active
                )

                db.add(new_category)
                await db.commit()
                await db.refresh(new_category)

                # Populate the response data
                responses.append({
                    "status_code": 201,
                    "status": "Successfully created category.",
                    "data": {
                        "cat_id": new_category.cat_id,
                        "name": new_category.name,
                        "is_active": new_category.is_active,
                        "created_on": new_category.created_on.isoformat(),
                        "updated_on": new_category.updated_on.isoformat() if new_category.updated_on else None,
                        "id": new_category.id
                    }
                })

            except Exception as e:
                logger.error(f"Error creating category '{
                            name}': {e}", exc_info=True)
                responses.append({
                    "status_code": 500,
                    "status": f"Failed to create category '{name}'.",
                    "data": None
                })

        return responses
    
    @staticmethod
    async def get_all_categories(db: AsyncSession, skip: int = 0, limit: int = 10):
        try:
            total_count_result = await db.execute(select(func.count()).select_from(Category))
            total_count = total_count_result.scalar()

            result = await db.execute(select(Category).order_by(desc(Category.id)).offset(skip).limit(limit))
            categories = result.scalars().all()

            return {
                "status": "success",
                "message": "Categories retrieved successfully.",
                "total_count": total_count,
                "data": [CategoryModel.from_orm(category) for category in categories]
            }
        except Exception as e:
            logger.error(f"Error retrieving categories: {str(e)}")
            return {
                "status": "failure",
                "message": f"Error retrieving categories: {str(e)}",
                "data": None
            }


    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: int):
        try:
            result = await db.execute(select(Category).where(Category.id == category_id))
            category = result.scalars().first()

            if category:
                return {
                    "status": "success",
                    "message": "Category retrieved successfully.",
                    "data": CategoryModel.from_orm(category)
                }
            else:
                return {
                    "status": "failure",
                    "message": "Category not found.",
                    "data": None
                }
        except Exception as e:
            logger.error(f"Error retrieving category by id: {str(e)}")
            return {
                "status": "failure",
                "message": f"Error retrieving category: {str(e)}",
                "data": None
            }


    @staticmethod
    async def update_category(db: AsyncSession, category_id: int, category_data: CategoryUpdateModel):
        try:
            result = await db.execute(select(Category).where(Category.id == category_id))
            category = result.scalars().first()

            if not category:
                return {
                    "status": "failure",
                    "message": "Category not found.",
                    "data": None
                }

            # Update fields if provided
            if category_data.name is not None:
                category.name = category_data.name
            if category_data.is_active is not None:
                category.is_active = category_data.is_active

            # Update 'updated_on' to the current system time
            category.updated_on = datetime.now()

            db.add(category)  # Add to session
            await db.commit()  # Commit changes

            return {
                "status": "success",
                "message": "Category updated successfully.",
                "data": CategoryModel.from_orm(category)
            }
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            return {
                "status": "failure",
                "message": f"Error updating category: {str(e)}",
                "data": None
            }
            
    @staticmethod
    async def soft_delete_category(db: AsyncSession, category_id: int):
        try:
            result = await db.execute(select(Category).where(Category.id == category_id))
            category = result.scalars().first()

            if category:
                category.is_active = False
                db.add(category)
                await db.commit()

                return {
                    "status": "success",
                    "message": "Category soft deleted successfully.",
                    "data": CategoryModel.from_orm(category)
                }
            else:
                return {
                    "status": "failure",
                    "message": "Category not found.",
                    "data": None
                }
        except Exception as e:
            logger.error(f"Error soft deleting category: {str(e)}")
            return {
                "status": "failure",
                "message": f"Error soft deleting category: {str(e)}",
                "data": None
            }

    @staticmethod
    async def get_categories(
        db: AsyncSession,
        cat_id: Optional[str] = None,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        try:
            query = select(Category)

            if cat_id:
                query = query.where(Category.cat_id == cat_id)
            if name:
                query = query.where(Category.name.ilike(f"%{name}%"))
            if is_active is not None:
                query = query.where(Category.is_active == is_active)

            total_count_result = await db.execute(select(func.count()).select_from(query))
            total_count = total_count_result.scalar()

            # Pagination
            query = query.offset(skip).limit(limit)
            result = await db.execute(query)
            categories = result.scalars().all()

            # Return response
            if categories:
                return {
                    "status": "success",
                    "message": "Categories retrieved successfully.",
                    "total_count": total_count,
                    "data": [CategoryModel.from_orm(category) for category in categories]
                }
            else:
                return {
                    "status": "failure",
                    "message": "Data not found.",
                    "total_count": total_count,
                    "data": []
                }
        except Exception as e:
            logger.error(f"Error retrieving categories: {str(e)}")
            return {
                "status": "failure",
                "message": f"Error retrieving categories: {str(e)}",
                "data": None
            }
