from app.models import Product
from app.backend.dao import BaseDAO


class ProductDAO(BaseDAO):
    model = Product

