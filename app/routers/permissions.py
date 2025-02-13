from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from app.models import User
from app.routers.auth import get_current_user
from app.dao import UserDAO

router = APIRouter(prefix='/permission', tags=['permission'])


@router.get('/temp')
async def get_users():
    users = await UserDAO.find_all()  # db.scalars(select(User))
    return users


@router.put('/update')
async def update_user():
    await UserDAO.update(filters=[User.username == 'string'],
                         is_admin=True,
                         is_supplier=False,
                         is_customer=False)
    return {'message': 'success updating'}


@router.patch('/')
async def supplier_permission(admin: Annotated[dict, Depends(get_current_user)],
                              user_id: int):
    if not admin.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    user = await UserDAO.find_by_id(user_id)  # db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')
    await UserDAO.update(filters=[User.id == user_id], is_supplier=not user.is_supplier)
    return {"status_code": status.HTTP_200_OK,
            "message": "User is now supplier" if user.is_supplier else "User is no longer supplier"}


@router.delete('/delete')
async def delete_user(admin: Annotated[dict, Depends(get_current_user)],
                      user_id: int):
    if not admin.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    user = await UserDAO.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')
    if user.is_admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='You cannot delete Admin')
    await UserDAO.update(filters=[User.id == user_id], is_active=not user.is_active)
    return {"status_code": status.HTTP_200_OK,
            "message": "User is activated" if user.is_active else "User is deleted"}
