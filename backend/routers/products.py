import enum
from fastapi import APIRouter,HTTPException,Path, Query
from sqlalchemy import func
from starlette import status
from database import db_dependency
from models import Product



router=APIRouter()



@router.get("/products/price-range/{range_id}",status_code=status.HTTP_200_OK)
def get_products_by_price_range(range_id: int, db: db_dependency):
    if range_id != 6:
        if range_id == 1:
            min_price, max_price = 0, 100
        elif range_id == 2:
            min_price, max_price = 100, 200
        elif range_id == 3:
            min_price, max_price = 200, 300
        elif range_id == 4:
            min_price, max_price = 300, 400
        elif range_id == 5:
            min_price, max_price = 400, 500
        else:
            raise HTTPException(status_code=400, detail="Invalid price range")

    
        products = db.query(Product).filter(Product.price >= min_price,Product.price<=max_price).all()
    else:
        products=db.query(Product).all()

    return products





@router.get("/products",status_code=status.HTTP_200_OK)
async def get_all_products(db:db_dependency):
    products=db.query(Product).all()
    if not products:
        raise HTTPException(status_code=404,detail="No products found")
    return products


@router.get("/products/{product_id}",status_code=status.HTTP_200_OK)
async def get_all_products(db:db_dependency,product_id:int =Path(gt=0)):
    product=db.query(Product).filter(Product.id==product_id).first()
    if not product:
        raise HTTPException(status_code=404,detail="No product found")
    return product



@router.get("/products/category/{category_name}",status_code=status.HTTP_200_OK)
async def get_all_products(db:db_dependency,category_name:str):
    normalize_category=category_name.replace(" ","").lower()
    products=db.query(Product).filter(func.lower(func.replace(Product.category," ",""))==normalize_category).all()
    if not products:
        raise HTTPException(status_code=404,detail="No product found")
    return products



