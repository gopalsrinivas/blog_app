from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from app.models.categories import Category
from app.schemas.categories import CategoryCreateModel, CategoryModel, CategoryUpdateModel
from app.core.logging import logger
from datetime import datetime


class CategoryService:

    @staticmethod
    async def generate_cat_id(db: AsyncSession) -> str:
        try:
            result = await db.execute(select(func.max(Category.cat_id)))
            max_cat_id = result.scalar_one_or_none()

            if max_cat_id is None:
                next_number = 1
            else:
                next_number = int(max_cat_id.split('__')[1]) + 1

            new_cat_id = f"cat__{next_number}"
            logger.info(f"Generated new category ID: {new_cat_id}")
            return new_cat_id
        except Exception as e:
            logger.error(f"Error generating category ID: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def create_categories(db: AsyncSession, names: list[str], is_active: bool) -> list[dict[str, any]]:
        responses = []
        existing_names = []

        # Check for existing categories first
        for name in names:
            existing_category = await db.execute(select(Category).where(Category.name == name))
            if existing_category.scalars().first():
                existing_names.append(name)

        # If there are existing categories, return an error response
        if existing_names:
            return [{
                "status_code": 400,
                "status": f"Categories already exist: {', '.join(existing_names)}",
                "data": None
            }]

        # Create new categories for names that don't exist
        for name in names:
            try:
                new_category = Category(
                    cat_id=await CategoryService.generate_cat_id(db),
                    name=name,
                    is_active=is_active
                )

                db.add(new_category)
                await db.commit()
                await db.refresh(new_category)

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
                logger.error(f"Failed to create category '{
                             name}': {str(e)}", exc_info=True)
                responses.append({
                    "status_code": 500,
                    "status": f"Failed to create category '{name}'.",
                    "data": None
                })

        return responses

    @staticmethod
    async def get_categories(db: AsyncSession, cat_id: Optional[str] = None, name: Optional[str] = None, is_active: Optional[bool] = None, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
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

            query = query.offset(skip).limit(limit)
            result = await db.execute(query)
            categories = result.scalars().all()

            logger.info("Categories retrieved successfully.")
            return {
                "status": "success",
                "message": "Categories retrieved successfully.",
                "total_count": total_count,
                "data": [CategoryModel.from_orm(category) for category in categories]
            }
        except Exception as e:
            logger.error(f"Error retrieving categories: {
                         str(e)}", exc_info=True)
            return {
                "status": "failure",
                "message": f"Error retrieving categories: {str(e)}",
                "data": None
            }

    @staticmethod
    async def get_all_categories(db: AsyncSession, skip: int = 0, limit: int = 10):
        try:
            total_count_result = await db.execute(select(func.count()).select_from(Category))
            total_count = total_count_result.scalar()

            result = await db.execute(select(Category).order_by(desc(Category.id)).offset(skip).limit(limit))
            categories = result.scalars().all()

            logger.info(
                f"All categories retrieved successfully. Total: {total_count}")
            return {
                "status": "success",
                "message": "Categories retrieved successfully.",
                "total_count": total_count,
                "data": [CategoryModel.from_orm(category) for category in categories]
            }
        except Exception as e:
            logger.error(f"Error retrieving all categories: {
                         str(e)}", exc_info=True)
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
                logger.info(f"Category retrieved successfully: {
                            category.name}")
                return {
                    "status": "success",
                    "message": "Category retrieved successfully.",
                    "data": CategoryModel.from_orm(category)
                }
            else:
                logger.warning(f"Category with ID {category_id} not found.")
                return {
                    "status": "failure",
                    "message": "Category not found.",
                    "data": None
                }
        except Exception as e:
            logger.error(f"Error retrieving category by id: {
                         str(e)}", exc_info=True)
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
                logger.warning(f"Category with ID {category_id} not found.")
                return {
                    "status": "failure",
                    "message": "Category not found.",
                    "data": None
                }

            if category_data.name is not None:
                category.name = category_data.name
            if category_data.is_active is not None:
                category.is_active = category_data.is_active

            category.updated_on = datetime.now()
            db.add(category)
            await db.commit()

            logger.info(f"Category updated successfully: {category.name}")
            return {
                "status": "success",
                "message": "Category updated successfully.",
                "data": CategoryModel.from_orm(category)
            }
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}", exc_info=True)
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

                logger.info(f"Category soft deleted successfully: {
                            category.name}")
                return {
                    "status": "success",
                    "message": "Category soft deleted successfully.",
                    "data": CategoryModel.from_orm(category)
                }
            else:
                logger.warning(f"Category with ID {
                               category_id} not found for soft delete.")
                return {
                    "status": "failure",
                    "message": "Category not found.",
                    "data": None
                }
        except Exception as e:
            logger.error(f"Error soft deleting category: {
                         str(e)}", exc_info=True)
            return {
                "status": "failure",
                "message": f"Error soft deleting category: {str(e)}",
                "data": None
            }
