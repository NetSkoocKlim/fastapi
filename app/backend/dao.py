from sqlalchemy import insert, select, update
from app.backend.db import async_session_maker
from app.models import Category
from typing import Optional


class BaseDAO:
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int, filters: list[bool] = [], **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).where(*filters).filter_by(id=model_id, **filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, filters: list[bool] = [], **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).where(*filters).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_one_or_none(cls, filters: list[bool] = [], **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).where(*filters).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update(cls, filters: list[bool] = [], **data):
        async with async_session_maker() as session:
            query = update(cls.model).where(*filters).values(**data)
            await session.execute(query)
            await session.commit()

