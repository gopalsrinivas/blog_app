from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from app.models.subcategories import Subcategory
from app.schemas.subcategories import SubcategoryCreateModel, SubcategoryUpdateModel
from app.core.logging import logging


async def generate_subcat_id(db: AsyncSession) -> str:
    try:
        result = await db.execute(select(func.max(Subcategory.subcat_id)))
        max_subcat_id = result.scalar_one_or_none()
        next_number = 1 if max_subcat_id is None else int(
            max_subcat_id.split('__')[1]) + 1
        return f"subcat__{next_number}"
    except Exception as e:
        logging.error(f"Error generating subcategory ID: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error generating subcategory ID")


async def create_subcategory(db: AsyncSession, subcategory_data: SubcategoryCreateModel):
    try:
        subcategories = []
        for name in subcategory_data.names:
            new_subcat_id = await generate_subcat_id(db)
            new_subcategory = Subcategory(
                category_id=subcategory_data.category_id,
                subcat_id=new_subcat_id,
                name=name,
                is_active=subcategory_data.is_active,
            )
            db.add(new_subcategory)
            subcategories.append(new_subcategory)

        await db.commit()
        for subcategory in subcategories:
            await db.refresh(subcategory)

        logging.info(f"Successfully created {
                     len(subcategories)} subcategories.")
        return subcategories
    except Exception as e:
        logging.error(f"Failed to create subcategories: {
                      str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to create subcategories")


async def get_all_subcategories(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(
            select(Subcategory).where(Subcategory.is_active == True).order_by(
                Subcategory.id.desc()).offset(skip).limit(limit)
        )
        subcategories = result.scalars().all()

        # Get the total count of active subcategories
        total_count_result = await db.execute(
            select(func.count(Subcategory.id)).where(
                Subcategory.is_active == True)
        )
        total_count = total_count_result.scalar()

        logging.info("Successfully retrieved all active subcategories.")
        return subcategories, total_count
    except Exception as e:
        logging.error(f"Failed to fetch subcategories: {
                      str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to fetch subcategories")


async def get_subcategory_by_id(db: AsyncSession, subcategory_id: int):
    try:
        result = await db.get(Subcategory, subcategory_id)
        if not result:
            logging.warning(f"Subcategory with ID {subcategory_id} not found.")
        return result
    except Exception as e:
        logging.error(f"Error retrieving subcategory by ID {
                      subcategory_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Error retrieving subcategory")


async def update_subcategory(db: AsyncSession, subcategory_id: int, subcategory_data: SubcategoryUpdateModel):
    try:
        subcategory = await get_subcategory_by_id(db, subcategory_id)
        if not subcategory:
            logging.warning(f"Subcategory with ID {subcategory_id} not found.")
            return None

        # Update fields as needed
        if subcategory_data.category_id is not None:
            subcategory.category_id = subcategory_data.category_id
        if subcategory_data.name is not None:
            subcategory.name = subcategory_data.name
        if subcategory_data.is_active is not None:
            subcategory.is_active = subcategory_data.is_active

        # Commit changes to the database
        await db.commit()
        await db.refresh(subcategory)

        logging.info(f"Subcategory with ID {
                     subcategory_id} updated successfully.")
        return subcategory
    except Exception as e:
        logging.error(f"Failed to update subcategory with ID {
                      subcategory_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to update subcategory")


async def soft_delete_subcategory(db: AsyncSession, subcategory_id: int):
    try:
        subcategory = await get_subcategory_by_id(db, subcategory_id)
        if not subcategory:
            logging.warning(f"Subcategory with ID {
                            subcategory_id} not found for soft delete.")
            return False

        # Set is_active to False for soft delete
        subcategory.is_active = False
        await db.commit()
        await db.refresh(subcategory)

        logging.info(f"Subcategory with ID {
                     subcategory_id} soft deleted successfully.")
        return subcategory
    except Exception as e:
        logging.error(f"Failed to soft delete subcategory with ID {
                      subcategory_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to soft delete subcategory")
