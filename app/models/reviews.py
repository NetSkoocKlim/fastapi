from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    rating_id = Column(Integer, ForeignKey('ratings.id'), nullable=False)
    comment = Column(String)
    comment_date = Column(Date)
    is_active = Column(Boolean, default=True)



