from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated

from app.models import *
from app.schemas import CreateCategory
from app.routers.auth import get_current_user
from app.dao import CategoryDAO

from slugify import slugify

router = APIRouter(prefix='/category', tags=['category'])


@router.get('/all_categories')
async def get_all_categories():
    return await CategoryDAO.find_all(filters=[Category.is_active])


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_category(created_category: Annotated[CreateCategory, Depends(CreateCategory)],
                          user: Annotated[dict, Depends(get_current_user)]):
    if not user.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    await CategoryDAO.add(name=created_category.name,
                          parent_id=created_category.parent_id,
                          slug=slugify(created_category.name))
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put('/update_category')
async def update_category(category_id: int,
                          updated_category: CreateCategory,
                          user: Annotated[dict, Depends(get_current_user)]):
    if not user.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    category = await CategoryDAO.find_by_id(category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )

    await CategoryDAO.update(filters=[Category.id == category_id],
                             name=updated_category.name,
                             slug=slugify(updated_category.name),
                             parent_id=updated_category.parent_id)

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category update is successful'
    }


@router.delete('/delete')
async def delete_category(category_id: int,
                          user: Annotated[dict, Depends(get_current_user)]):
    if not user.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    category = await CategoryDAO.find_by_id(category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    await CategoryDAO.update(filters=[category_id == Category.id], is_active=False)
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category delete is successful'
    }
