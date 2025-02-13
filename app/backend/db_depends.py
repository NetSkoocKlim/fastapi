from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.db import async_session_maker


async def get_db():
    async with async_session_maker() as session:
        yield session
