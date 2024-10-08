import logging
import pytz
from sqlalchemy import select, join, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from app.models.blog import Blog
from app.models.categories import Category
from app.models.subcategories import Subcategory
from app.schemas.blog import *
from app.core.logging import logging
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from pathlib import Path
import os
from typing import Optional
import shutil
from fastapi import UploadFile
from app.core.config import MEDIA_DIR
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound

async def generate_blog_id(db: AsyncSession) -> str:
    try:
        result = await db.execute(select(func.max(Blog.id)))
        max_id = result.scalar_one_or_none()
        new_id = (max_id + 1) if max_id is not None else 1
        return f"blog_{new_id}"
    except Exception as e:
        logging.error(f"Error generating Blog ID: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating Blog ID")

async def create_blog(db: AsyncSession, blog_data: dict, image_path: str = None):
    try:
        # Validate Category ID
        category_exists = await db.scalar(select(func.count()).select_from(Category).where(Category.id == blog_data["category_id"]))
        if not category_exists:
            logging.warning(f"Category ID {blog_data['category_id']} not found")
            raise HTTPException(status_code=400, detail="Category ID not found")

        # Validate Subcategory ID
        subcategory_exists = await db.scalar(
            select(func.count()).select_from(Subcategory)
            .where(Subcategory.id == blog_data["subcategory_id"]))
        if not subcategory_exists:
            logging.warning(f"Subcategory ID {blog_data['subcategory_id']} not found")
            raise HTTPException(status_code=400, detail="Subcategory ID not found")

        # Check if the blog title already exists
        title_exists = await db.scalar(
            select(func.count()).select_from(Blog)
            .where(Blog.title == blog_data["title"]))
        if title_exists:
            logging.warning(f"Blog title '{blog_data['title']}' already exists")
            raise HTTPException(status_code=400, detail="Blog title already exists")

        # Generate a unique blog ID
        new_blog_id = await generate_blog_id(db)

        # Create a new Blog instance using ORM
        new_blog = Blog(
            blog_id=new_blog_id,
            title=blog_data["title"],
            category_id=blog_data["category_id"],
            subcategory_id=blog_data["subcategory_id"],
            content=blog_data["content"],
            image=image_path,
            is_active=blog_data["is_active"],
            created_on=datetime.now(),
            updated_on=None
        )

        db.add(new_blog)
        await db.commit()

        # Refresh the object to get the updated instance
        await db.refresh(new_blog)

        logging.info(f"Blog '{blog_data['title']}' created successfully with ID {new_blog_id}")
        return new_blog

    except IntegrityError as e:
        await db.rollback()
        logging.error(f"IntegrityError occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"IntegrityError: {str(e)}")

    except Exception as exc:
        await db.rollback()
        logging.error(f"Unexpected error occurred: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(exc)}")

    finally:
        await db.close()
        

async def get_all_blog_detail(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                Subcategory.id.label("subcategory_id"),
                Subcategory.name.label("subcategory_name"),
                Blog.id.label("id"),
                Blog.blog_id.label("blog_id"),
                Blog.title.label("blog_title"),
                Blog.content.label("blog_content"),
                Blog.image.label("blog_image"),
                Blog.is_active.label("is_active"),
                Blog.created_on.label("created_on"),
                Blog.updated_on.label("updated_on")
            )
            .select_from(
                 join(Category, Subcategory, Category.id == Subcategory.category_id)
                .join(Blog, Subcategory.id == Blog.subcategory_id)
            )
            .where(Blog.is_active == True)
            .order_by(Blog.id.desc())
            .offset(skip)
            .limit(limit)
        )
        blog_details = result.all()

        total_count_result = await db.execute(
            select(func.count(Blog.id))
            .select_from(
                join(Category, Subcategory, Category.id == Subcategory.category_id)
                .join(Blog, Subcategory.id == Blog.subcategory_id)
            )
            .where(Blog.is_active == True)
        )
        total_count = total_count_result.scalar()

        logging.info("Successfully retrieved all active blogs with details.")
        return blog_details, total_count

    except Exception as e:
        logging.error(f"Failed to fetch blog details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch blog details")
        

async def get_blog_detail_by_id(db: AsyncSession, blog_detail_id: int):
    try:
        # Perform the join between categories, subcategories, and blog for the specific blog ID
        result = await db.execute(
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                Subcategory.id.label("subcategory_id"),
                Subcategory.name.label("subcategory_name"),
                Blog.id.label("id"),
                Blog.blog_id.label("blog_id"),
                Blog.title.label("blog_title"),
                Blog.content.label("blog_content"),
                Blog.image.label("blog_image"),
                Blog.is_active.label("is_active"),
                Blog.created_on.label("created_on"),
                Blog.updated_on.label("updated_on")
            )
            .select_from(
                join(Category, Subcategory, Category.id == Subcategory.category_id)
                .join(Blog, Subcategory.id == Blog.subcategory_id)
            )
            .where(Blog.id == blog_detail_id)
        )

        blog_detail = result.fetchone()

        if not blog_detail:
            logging.warning(f"Blog with ID {blog_detail_id} not found.")
            raise HTTPException(status_code=404, detail=f"Blog with ID {blog_detail_id} not found")

        # Check if the blog is active
        if not blog_detail.is_active:
            logging.info(f"Blog with ID {blog_detail_id} is not active.")
            return {
                "status_code": 200,
                "message": "Blog is not active",
                "data": {
                    "is_active": blog_detail.is_active,
                    "blog_title": blog_detail.blog_title
                }
            }

        logging.info(f"Successfully retrieved blog with ID {blog_detail_id}.")
        return blog_detail

    except Exception as e:
        logging.error(f"Error retrieving blog detail with ID {blog_detail_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving Blog")


async def handle_image_update(blog, new_image: UploadFile):
    existing_image_path = os.path.join(MEDIA_DIR, blog.image)

    # Delete old image if it exists
    if blog.image and os.path.exists(existing_image_path):
        try:
            os.remove(existing_image_path)
            logging.info(f"Old image {blog.image} deleted successfully.")
        except Exception as e:
            logging.error(f"Failed to delete old image {blog.image}: {str(e)}")

    # Save the new image
    new_image_filename = f"blog_{blog.id}_{new_image.filename}"
    new_image_path = os.path.join(MEDIA_DIR, new_image_filename)

    try:
        with open(new_image_path, "wb") as buffer: shutil.copyfileobj(new_image.file, buffer)

        # Update the blog image field with just the new image filename
        blog.image = new_image_filename
        logging.info(f"New image {new_image_filename} saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save new image {new_image_filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload new image")


async def update_blog_details(db: AsyncSession, blog_detail_id: int, blog_data: BlogUpdateModel, new_image: UploadFile = None):
    # Retrieve the blog entry by ID
    blog = await db.get(Blog, blog_detail_id)

    # Raise an exception if the blog entry does not exist
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with ID {blog_detail_id} not found.")

    # Prepare the updated fields
    updated_fields = {
        "category_id": blog_data.category_id if blog_data.category_id is not None else blog.category_id,
        "subcategory_id": blog_data.subcategory_id if blog_data.subcategory_id is not None else blog.subcategory_id,
        "title": blog_data.title,
        "content": blog_data.content,
        "is_active": blog_data.is_active,
        "updated_on": datetime.now()
    }

    # Update the blog's attributes with new values
    for key, value in updated_fields.items():
        setattr(blog, key, value)

    # Handle new image if provided
    if new_image:
        await handle_image_update(blog, new_image)

    # Commit the changes to the database
    try:
        await db.commit()
        await db.refresh(blog)
        return blog
    except Exception as e:
        await db.rollback()
        logging.error(f"Error updating blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update blog")
    

async def soft_delete_blog_detail(db: AsyncSession, blog_detail_id: int):
    try:
        result = await db.execute(
            select(Blog).where(Blog.id == blog_detail_id)
        )
        blog_detail = result.scalars().first()

        if not blog_detail:
            logging.warning(
                f"Blog with ID {blog_detail_id} not found for soft delete.")
            raise HTTPException(status_code=404, detail="Blog not found.")

        # Set is_active to False for soft delete
        blog_detail.is_active = False
        db.add(blog_detail)
        await db.commit()
        await db.refresh(blog_detail)
        
        logging.info(f"Blog with ID {blog_detail_id} soft deleted successfully.")
        return blog_detail

    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to soft delete blog with ID {blog_detail_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to soft delete blog")

async def get_blogdetail_by_subcategory_id(db: AsyncSession, subcategory_id: int, skip: int = 0, limit: int = 10):
    try:
        logging.info(f"Fetching blog details for subcategory ID: {subcategory_id}.")

        # Query to get the subcategory along with its associated blogs and category
        query = (
            select(Subcategory)
            .options(
                joinedload(Subcategory.blogs),
                joinedload(Subcategory.category)
            )
            .where(Subcategory.id == subcategory_id)
        )

        # Execute the query and get the result
        result = await db.execute(query)

        # Retrieve the unique subcategory result
        subcategory = result.unique().scalar_one_or_none()

        # Check if the subcategory exists
        if not subcategory:
            logging.warning(f"Subcategory with ID {subcategory_id} not found.")
            raise HTTPException(status_code=404, detail="Subcategory not found.")

        # Filter blogs to include only those that are active
        active_blogs = [blog for blog in subcategory.blogs if blog.is_active]

        logging.info(f"Retrieved {len(active_blogs)} active blogs for subcategory ID: {subcategory_id}.")

        # Implement pagination for active blogs
        paginated_blogs = active_blogs[skip: skip + limit]

        # Count total active blogs
        total_active_blogs_count = len(active_blogs)

        # Count total blogs in the subcategory (active + inactive)
        total_all_blogs_count = len(subcategory.blogs)

        return {
            "subcategory_id": subcategory.id,
            "subcategory_name": subcategory.name,
            "category_id": subcategory.category.id,
            "category_name": subcategory.category.name,
            "blogs": paginated_blogs,
            "total_active_blogs": total_active_blogs_count,
            "total_all_blogs": total_all_blogs_count
        }

    except Exception as e:
        logging.error(f"Error fetching blogs for subcategory ID {subcategory_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch blogs.")
