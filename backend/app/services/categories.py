from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.categories import *
from app.schemas.categories import *
from app.core.logging import logger
from sqlalchemy import func, select, desc


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
