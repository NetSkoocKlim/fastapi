from pydantic import BaseModel, Field


class SProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category_id: int

    


class SCategory(BaseModel):
    name: str
    parent_id: int = Field(default=-1)


class SUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class SReview(BaseModel):
    product_id: int
    grade: int
    comment: str

