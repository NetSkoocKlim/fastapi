from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import category, products, auth, permissions, reviews, pages

app = FastAPI()
app_v1 = FastAPI(title='Store API')

@app.get("/")
async def welcome() -> dict:
    return {"message": "My e-commerce app"}

app.mount('/v1', app_v1)
app_v1.mount('/static', StaticFiles(directory='app/static'), name='static')

app_v1.include_router(pages.router)
app_v1.include_router(auth.router)
app_v1.include_router(category.router)
app_v1.include_router(products.router)
app_v1.include_router(permissions.router)
app_v1.include_router(reviews.router)


