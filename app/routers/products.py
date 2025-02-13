from fastapi import APIRouter
from typing import Annotated
from app.schemas import CreateProduct
from fastapi import status, Depends, HTTPException
from app.models import Product
from app.routers.auth import get_current_user
from app.dao import ProductDAO, CategoryDAO
from slugify import slugify

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products():
    products = await ProductDAO.find_all(filters=[Product.stock > 0,
                                                  Product.is_active])  # await db.scalars(select(Product).where(Product.stock > 0, Product.is_active))
    if products:
        return products
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Products not found")


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(
        created_product: Annotated[Product, Depends(CreateProduct)],
        user: Annotated[dict, Depends(get_current_user)]):
    if not user.get('is_admin') or not user.get('is_supplier'):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail='You must have admin or supplier role to use this method')
    await ProductDAO.add(
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
    )
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/{category_slug}')
async def product_by_category(category_slug: str):
    category = await CategoryDAO.find_one_or_none(
        slug=category_slug)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    subcategories = await CategoryDAO.find_all(parent_id=category.id)
    subcategories = list([subcategory.id for subcategory in subcategories])
    products = await ProductDAO.find_all(filters=[
        Product.category_id.in_([category.id] + subcategories),
        Product.stock > 0, Product.is_active])
    if products:
        return products
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Products not found")


@router.get('/detail/{product_slug}')
async def product_detail(product_slug: str):
    product = await ProductDAO.find_one_or_none(slug=product_slug)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put('/detail/{product_slug}')
async def update_product(product_slug: str,
                         updated_product: Annotated[Product, Depends(CreateProduct)],
                         user: Annotated[dict, Depends(get_current_user)]):
    product = await ProductDAO.find_one_or_none(slug=product_slug)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if not user.get('is_admin') or not user.get('is_supplier') or not product.supplier_id != user.get('id'):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail='You must be admin or supplier to use this method')
    await ProductDAO.update(filters=[product.id == Product.id],
                            name=updated_product.name,
                            description=updated_product.description,
                            price=updated_product.price,
                            image_url=updated_product.image_url,
                            stock=updated_product.stock,
                            category_id=updated_product.category_id,
                            )
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product update is successful'
    }


@router.delete('/delete')
async def delete_product(product_slug: str,
                         user: Annotated[dict, Depends(get_current_user)]):
    product = await ProductDAO.find_one_or_none(slug=product_slug)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if not user.get('is_admin') or not user.get('is_supplier') or not product.supplier_id != user.get('id'):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail='You must be admin or supplier to use this method')
    await ProductDAO.update(filters=[product.id == Product.id],
                            is_active=False
                            )
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product delete is successful'
    }
