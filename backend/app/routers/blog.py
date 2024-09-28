from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.blog import *
from app.core.database import get_db
from app.schemas.blog import *
from typing import Optional
from pathlib import Path
import shutil
import os
import uuid
from app.core.logging import logging
from datetime import datetime
from app.core.config import MEDIA_DIR

router = APIRouter()


@router.post("/create_blog", response_model=BlogResponseModel, summary="Create new Blog")
async def create_blog_api(
    category_id: Optional[int] = Form(None),
    subcategory_id: Optional[int] = Form(None),
    title: str = Form(...),
    content: str = Form(...),
    is_active: Optional[bool] = Form(True),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Generate a unique blog ID
        new_blog_id = await generate_blog_id(db)

        # Prepare the image path if an image is provided
        image_path = None
        if image:
            image_extension = image.filename.split(".")[-1]
            # Get the original filename without extension
            original_filename = os.path.splitext(image.filename)[0]
            image_filename = f"{new_blog_id}_{original_filename}.{
                image_extension}"  # Format: (blogid)originalfilename.ext
            image_path = os.path.join(MEDIA_DIR, image_filename)

            # Create the media directory if it doesn't exist
            os.makedirs(MEDIA_DIR, exist_ok=True)
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            # Log the image path being saved
            logging.info(f"Image path being saved: {image_path}")

        # Create the blog entry with the generated blog ID
        new_blog = await create_blog(db, {
            "category_id": category_id,
            "subcategory_id": subcategory_id,
            "title": title,
            "content": content,
            "is_active": is_active,
        }, image_path=image_path)

        # Prepare the response
        response_data = BlogResponseModel.from_orm(new_blog)

        return response_data

    except HTTPException as http_exc:
        logging.error(f"HTTP error while creating blog: {
                      str(http_exc.detail)}")
        raise http_exc
    except Exception as exc:
        logging.error(f"Unexpected error occurred: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(exc)}"
        )


@router.get("/all/", response_model=dict, summary="List of Blog Details")
async def get_blog_details(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    db: AsyncSession = Depends(get_db)
):
    try:
        blog_details, total_count = await get_all_blog_detail(db, skip=skip, limit=limit)

        # # Handle images properly: Convert paths to URLs
        # # Replace with your actual media server or base URL
        # base_url = MEDIA_DIR

        # Flatten the result into a list of dictionaries
        data = [
            {
                "category_id": category_id,
                "category_name": category_name,
                "subcategory_id": subcategory_id,
                "subcategory_name": subcategory_name,
                "id": id,
                "blog_id": blog_id,
                "blog_title": blog_title,
                "blog_content": blog_content,
                # Generate the image URL if image exists
                "blog_image": f"{blog_image}" if blog_image else None,
                "is_active": is_active,
                "created_on": created_on,
                "updated_on": updated_on
            }
            for category_id, category_name, subcategory_id, subcategory_name, id, blog_id, blog_title, blog_content, blog_image, is_active, created_on, updated_on in blog_details
        ]

        logging.info("Successfully retrieved all blog details.")
        return {
            "status_code": 200,
            "message": "Blog details retrieved successfully",
            "total_count": total_count,
            "data": data
        }
    except Exception as e:
        logging.error(f"Failed to fetch blog details: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch blog details"
        )

@router.get("/{blog_detail_id}", response_model=dict, summary="Retrieve a Blog by ID")
async def get_blog_by_id_route(blog_detail_id: int, db: AsyncSession = Depends(get_db)):
    try:
        blog_detail = await get_blog_detail_by_id(db, blog_detail_id)

        # Check if blog_detail is a dictionary and contains "status_code"
        if isinstance(blog_detail, dict) and "status_code" in blog_detail:
            return blog_detail  # Return early if it's an inactive blog response

        # If blog_detail is a Row object, manually construct response data
        if blog_detail:
            data = {
                "category_id": blog_detail.category_id,
                "category_name": blog_detail.category_name,
                "subcategory_id": blog_detail.subcategory_id,
                "subcategory_name": blog_detail.subcategory_name,
                "id": blog_detail.id,
                "blog_id": blog_detail.blog_id,
                "blog_title": blog_detail.blog_title,
                "blog_content": blog_detail.blog_content,
                "blog_image": blog_detail.blog_image,  # Include the image
                "is_active": blog_detail.is_active,
                "created_on": blog_detail.created_on,
                "updated_on": blog_detail.updated_on
            }

            logging.info(f"Blog details retrieved: {blog_detail.blog_title}")
            return {
                "status_code": 200,
                "message": "Blog detail retrieved successfully",
                "data": data
            }
        else:
            logging.warning(f"Blog with ID {blog_detail_id} not found.")
            raise HTTPException(status_code=404, detail=f"Blog with ID {
                                blog_detail_id} not found")

    except HTTPException as http_exc:
        logging.error(f"HTTP error occurred: {str(http_exc.detail)}")
        raise http_exc  # Reraise the HTTPException for FastAPI to handle
    except Exception as e:
        logging.error(f"Failed to fetch Blog details: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch Blog details"
        )


@router.put("/{blog_detail_id}", response_model=BlogResponseModel, summary="Update a Blog by ID")
async def update_blog_route(
    blog_detail_id: int,
    title: str = Form(...),
    content: str = Form(...),
    is_active: bool = Form(...),
    category_id: Optional[int] = Form(None),
    subcategory_id: Optional[int] = Form(None),
    new_image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    existing_blog = await db.get(Blog, blog_detail_id)
    if not existing_blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    blog_data = BlogUpdateModel(
        id=blog_detail_id,
        category_id=category_id,
        subcategory_id=subcategory_id,
        blog_id=existing_blog.blog_id,
        title=title,
        content=content,
        is_active=is_active
    )

    updated_blog = await update_blog_details(db, blog_detail_id, blog_data, new_image)

    return BlogResponseModel(
        id=updated_blog.id,
        category_id=updated_blog.category_id,
        subcategory_id=updated_blog.subcategory_id,
        blog_id=updated_blog.blog_id,
        title=updated_blog.title,
        content=updated_blog.content,
        image=updated_blog.image,
        is_active=updated_blog.is_active,
        created_on=updated_blog.created_on,
        updated_on=updated_blog.updated_on
    )


@router.delete("/{blogdetail_id}", response_model=dict, summary="Delete a Blog details by ID")
async def delete_blog_detail_route(blogdetail_id: int, db: AsyncSession = Depends(get_db)):
    try:
        delete_blogdetail = await soft_delete_blog_detail(db, blogdetail_id)
        if not delete_blogdetail:
            raise HTTPException(
                status_code=404, detail="Blog detail ID not found")

        logging.info(f"Blog detail soft deleted with ID: {blogdetail_id}")
        return {
            "status_code": 200,
            "message": "Blog detail soft deleted successfully",
            "data": {
                "id": delete_blogdetail.id,
                "is_active": delete_blogdetail.is_active
            }
        }

    except Exception as e:
        logging.error(f"Failed to soft delete blog detail with ID {
                      blogdetail_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to soft delete blog detail")
