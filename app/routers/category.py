from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.db_depends import get_db
from typing import Annotated

from app.models import *
from sqlalchemy import insert, select, update
from app.schemas import CreateCategory
from app.routers.auth import get_current_user

from slugify import slugify

router = APIRouter(prefix='/category', tags=['category'])


@router.get('/all_categories')
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    categories = await db.scalars(select(Category).where(Category.is_active))
    return categories.all()


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_category(db: Annotated[AsyncSession, Depends(get_db)], created_category: CreateCategory,
                          user: Annotated[dict, Depends(get_current_user)]):
    if not user.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    await db.execute(insert(Category).values(name=created_category.name,
                                             parent_id=created_category.parent_id,
                                             slug=slugify(created_category.name)))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put('/update_category')
async def update_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: int,
                          updated_category: CreateCategory, user: Annotated[dict, Depends(get_current_user)]):
    if not user.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    category = await db.scalar(select(Category).where(Category.id == category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )

    await db.execute(update(Category).where(Category.id == category_id).values(
        name=updated_category.name,
        slug=slugify(updated_category.name),
        parent_id=updated_category.parent_id))

    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category update is successful'
    }


@router.delete('/delete')
async def delete_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: int,
                          user: Annotated[dict, Depends(get_current_user)]):
    if not user.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    category = await db.scalar(select(Category).where(Category.id == category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    await db.execute(update(Category).where(Category.id == category_id).values(is_active=False))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category delete is successful'
    }
