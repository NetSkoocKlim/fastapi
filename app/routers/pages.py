from fastapi import APIRouter, Request
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

from app.routers.category import get_all_categories, update_category

router = APIRouter(prefix="/pages", tags=["pages"])

templates = Jinja2Templates(directory="app/templates")

@router.get("/categories", response_class=HTMLResponse)
async def get_categories_pages(request: Request,
                               categories: Annotated[dict, Depends(get_all_categories)]):
    return templates.TemplateResponse("categories.html", {"request": request,
                                                          "categories": categories})