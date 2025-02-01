from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.db_depends import get_db
from app.models import User
from app.routers.auth import get_current_user
from sqlalchemy import select, update
from app.schemas import CreateUser
router = APIRouter(prefix='/permission', tags=['permission'])


@router.get('/temp')
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    users = await db.scalars(select(User))
    return users.all()


@router.put('/update')
async def update_user(db: Annotated[AsyncSession, Depends(get_db)]):
    await db.execute(update(User).where(User.username == 'string').values(is_admin=True,
                                                                            is_supplier=False,
                                                                            is_customer=False))
    await db.commit()
    return {'message': 'success updating'}


@router.patch('/')
async def supplier_permission(db: Annotated[AsyncSession, Depends(get_db)], admin: Annotated[dict,
                                                                                             Depends(get_current_user)],
                                   user_id: int):
    if not admin.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')
    await db.execute(update(User).where(User.id == user_id).values(is_supplier=not user.is_supplier))
    await db.commit()
    return {"status_code": status.HTTP_200_OK,
            "message": "User is now supplier" if user.is_supplier else "User is no longer supplier"}


@router.delete('/delete')
async def delete_user(db: Annotated[AsyncSession, Depends(get_db)], admin: Annotated[dict, Depends(get_current_user)],
                                   user_id: int):
    if not admin.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    user: User = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')
    if user.is_admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='You cannot delete Admin')

    await db.execute(update(User).where(User.id == user_id).values(is_active=not user.is_active))
    await db.commit()
    return {"status_code": status.HTTP_200_OK,
            "message": "User is activated" if user.is_active else "User is deleted"}

