from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas import CreateUser
from app.backend.db_depends import get_db

from typing import Annotated

from passlib.context import CryptContext

router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
security = HTTPBasic()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], created_user: CreateUser):
    await db.execute(insert(User).values(first_name=created_user.first_name,
                                         last_name=created_user.last_name,
                                         username=created_user.username,
                                         email=created_user.email,
                                         hashed_password=bcrypt_context.hash(created_user.password),
                                         ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


async def authanticate_user(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str):
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password) or user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


