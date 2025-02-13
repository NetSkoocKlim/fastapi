from app.models import Rating, Review
from app.backend.dao import BaseDAO
from app.backend.db import async_session_maker

from sqlalchemy import select, insert, update


class ReviewDAO(BaseDAO):
    model = Review

    @classmethod
    async def find_all(cls, filters: list[bool] = [], **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model, Rating).join(Rating).where(*filters).filter_by(**filter_by)
            result = await session.execute(query)
            return [{'review': review, 'rating': rating} for review, rating in result.all()]

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            rating_add_query = insert(Rating).values(user_id=data['user_id'],
                                                     product_id=data['product_id'],
                                                     grade=data['grade']).returning(Rating.id)
            rating_id = (await session.execute(rating_add_query)).scalar()
            review_add_query = insert(cls.model).values(
                user_id=data['user_id'],
                product_id=data['product_id'],
                rating_id=rating_id,
                comment=data['comment'],
                comment_date=data['comment_date']
            )
            await session.execute(review_add_query)
            await session.commit()

    @classmethod
    async def delete(cls, review_id, rating_id):
        async with async_session_maker() as session:
            review_update_query = update(cls.model).where(cls.id == review_id).values(is_active=False)
            await session.execute(review_update_query)
            rating_update_query = update(Rating).where(Rating.id == rating_id).values(is_active=False)
            await session.execute(rating_update_query)
            await session.commit()
