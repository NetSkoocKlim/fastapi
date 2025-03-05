import datetime

from fastapi import APIRouter, Depends, status, HTTPException
from app.models import Review, Rating, Product
from app.schemas import SReview
from app.routers.auth import get_current_user
from app.dao import ReviewDAO, ProductDAO

from typing import Annotated

router = APIRouter(prefix='/preview', tags=['reviews'])


@router.get('/all_reviews')
async def get_all_reviews():
    return await ReviewDAO.find_all(filters=[Review.is_active, Rating.is_active])


@router.get('/products_reviews')
async def get_product_reviews(product_id: int):
    return await ReviewDAO.find_all(filters=[Review.is_active, Rating.is_active], product_id=product_id)


@router.post('/add_review')
async def post_review(review: Annotated[SReview, Depends()],
                      user: Annotated[dict, Depends(get_current_user)]):
    await ReviewDAO.add(user_id=user.get('id'),
                        product_id=review.product_id,
                        grade=review.grade,
                        comment=review.comment,
                        comment_date=datetime.datetime.now(),
                        )
    review_count = len(tuple(await get_product_reviews(review.product_id)))
    await ProductDAO.update(filters=[Product.id == review.product_id],
                            rating=(Product.rating + review.grade) / review_count)
    return {
        "status_code": status.HTTP_200_OK,
        "message": "Review is created"
    }


@router.delete('/delete_reviews')
async def delete_review(review_id: int,
                        user: Annotated[dict, Depends(get_current_user)]):
    if not user.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail='You must be admin to perform this action')
    review = await ReviewDAO.find_by_id(review_id, filters=[
        Review.is_active])
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Review not found')
    await ReviewDAO.delete(review_id, review.rating_id)
    return {"status_code": status.HTTP_200_OK,
            "message": "Review has been deleted"}
