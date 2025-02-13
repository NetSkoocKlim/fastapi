from app.models import User
from app.backend.dao import BaseDAO


class UserDAO(BaseDAO):
    model = User
