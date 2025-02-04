import datetime

from fastapi import APIRouter, Depends, status, HTTPException
from app.backend.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from app.models import Review, Rating, Product
from app.schemas import CreateReview
from app.routers.auth import get_current_user

from typing import Annotated

router = APIRouter(prefix='/preview', tags=['reviews'])


@router.get('/all_reviews')
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.execute(select(Review, Rating).join(Rating).where(Review.is_active, Rating.is_active))
    return [{"review": review, "rating": rating} for review, rating in reviews.all()]


@router.get('/products_reviews')
async def get_product_reviews(db: Annotated[AsyncSession, Depends(get_db)],
                              product_id: int):
    reviews = await db.execute(select(Review, Rating).join(Rating).where(Review.is_active, Review.product_id==product_id))
    return [{"review": review, "rating": rating} for review, rating in reviews.all()]


@router.post('/add_review')
async def post_review(db: Annotated[AsyncSession, Depends(get_db)],
                      review: Annotated[CreateReview, Depends()],
                      user: Annotated[dict, Depends(get_current_user)]):
    rating_id = (await db.execute(insert(Rating).values(
        user_id=user.get('id'),
        product_id=review.product_id,
        grade=review.grade,
    ).returning(Rating.id))).scalar()
    await db.execute(insert(Review).values(
        user_id=user.get('id'),
        product_id=review.product_id,
        rating_id=rating_id,
        comment=review.comment,
        comment_date=datetime.datetime.now(),
    ))
    await db.commit()
    review_count = len(tuple(await get_product_reviews(db, review.product_id)))
    await db.execute(update(Product).where(Product.id == review.product_id).values(rating=(Product.rating + review.grade) / review_count))
    await db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "message": "Review is created"
    }


@router.delete('/delete_reviews')
async def delete_review(db: Annotated[AsyncSession, Depends(get_db)], review_id: int,
                        user: Annotated[dict, Depends(get_current_user)]):
    if not user.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail='You must be admin to perform this action')
    review = await db.scalar(select(Review).where(Review.is_active, Review.id == review_id))
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Review not found')
    await db.execute(update(Review).where(Review.id == review_id).values(is_active=False))
    await db.execute(update(Rating).where(Rating.id == review.rating_id).values(is_active=False))
    await db.commit()
    return {"status_code": status.HTTP_200_OK,
            "message": "Review has been deleted"}








