from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.categories import Category
from app.schemas.categories import CategoryCreateModel
from app.core.logging import logger
from fastapi import HTTPException, status


def generate_cat_id(category_count: int) -> str:
    return f"cat__{str(category_count + 1).zfill(3)}"


class CategoryService:

    @staticmethod
    async def create_category(db: AsyncSession, category_data: CategoryCreateModel) -> dict:
        try:
            # Check if the category name already exists
            existing_category = await db.execute(
                select(Category).where(Category.name == category_data.name)
            )
            if existing_category.scalars().first():
                # Return custom response for existing category
                return {
                    "status": "Category name already exists.",
                    "data": None,
                    "status_code": 400
                }

            # Generate a new category ID
            result = await db.execute(select(Category))
            category_count = len(result.scalars().all())

            new_category = Category(
                cat_id=generate_cat_id(category_count),
                name=category_data.name,
                is_active=category_data.is_active
            )

            db.add(new_category)
            await db.commit()
            await db.refresh(new_category)

            # Return success response
            return {
                "status": "Successfully created category.",
                "data": new_category,
                "status_code": 201
            }

        except Exception as e:
            # Log the error
            logger.error(f"Error creating category: {e}", exc_info=True)
            # Return internal server error response
            return {
                "status": "Failed to create category.",
                "data": None,
                "status_code": 500
            }
