from fastapi import APIRouter
from typing import Annotated, cast
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.db_depends import get_db
from app.schemas import CreateProduct
from fastapi import status, Depends, HTTPException, Body
from sqlalchemy import insert, select, update, delete
from app.models import Product, Category, User
from app.routers.auth import get_current_user
from slugify import slugify

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).where(Product.stock > 0, Product.is_active))
    products = products.all()
    if products:
        return products
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Products not found")


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[AsyncSession, Depends(get_db)],
                         created_product: Annotated[Product, Depends(CreateProduct)],
                         user: Annotated[dict, Depends(get_current_user)]):
    if not user.get('is_admin') or not user.get('is_supplier'):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail='You must have admin or supplier role to use this method')
    await db.execute(insert(Product).values(
        name=created_product.name,
        slug=slugify(created_product.name),
        description=created_product.description,
        price=created_product.price,
        image_url=created_product.image_url,
        stock=created_product.stock,
        category_id=created_product.category_id,
        supplier_id=user.get('id'),
        rating=0.0,
        is_active=True
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/{category_slug}')
async def product_by_category(category_slug: str, db: Annotated[AsyncSession, Depends(get_db)]):
    category = await db.scalar(select(Category).where(category_slug == Category.slug))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    subcategories = await db.scalars(select(Category.id).where(cast("ColumnElement[bool]",
                                                              category.id == Category.parent_id)))
    subcategories = list(subcategories.all())
    products = await db.scalars(select(Product).where(Product.category_id.in_([category.id] + subcategories), Product.stock > 0,
                                                Product.is_active))
    products = products.all()
    if products:
        return products
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Products not found")


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         updated_product: Annotated[Product, Depends(CreateProduct)],
                         user: Annotated[dict, Depends(get_current_user)]):
    product: Product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if not user.get('is_admin') or not user.get('is_supplier') or not product.supplier_id != user.get('id'):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail='You must be admin or supplier to use this method')

    await db.execute(update(Product).where(cast("ColumnElement[bool]",
                                                              product.id == Product.id)).values(
        name=updated_product.name,
        description=updated_product.description,
        price=updated_product.price,
        image_url=updated_product.image_url,
        stock=updated_product.stock,
        category_id=updated_product.category_id,
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product update is successful'
    }


@router.delete('/delete')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         user: Annotated[dict, Depends(get_current_user)]):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if not user.get('is_admin') or not user.get('is_supplier') or not product.supplier_id != user.get('id'):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail='You must be admin or supplier to use this method')

    await db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product delete is successful'
    }
