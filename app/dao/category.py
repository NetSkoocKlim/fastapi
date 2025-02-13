from app.models import Category
from app.backend.dao import BaseDAO


class CategoryDAO(BaseDAO):
    model = Category

