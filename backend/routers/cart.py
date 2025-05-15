import enum
from fastapi import APIRouter,HTTPException,Path, Query
from sqlalchemy import func
from starlette import status
from database import db_dependency
from models import Product,Cart,CartItem
from .auth import user_dependency



router=APIRouter()


@router.post("/cart/addtocart/{product_id}",status_code=status.HTTP_201_CREATED)
async def add_to_cart(db:db_dependency,userdata:user_dependency,product_id:int= Path(gt=0)):
    userId=userdata["id"]
    if not userId:
        raise HTTPException(status_code=401,detail="Unauthorized error")
    cart=db.query(Cart).filter(Cart.user_id==userId).first()
    if not cart:
        cart=Cart(user_id=userId)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    product=db.query(Product).filter(Product.id==product_id).first()
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    
    cartItem=db.query(CartItem).filter(CartItem.cart_id==cart.id,CartItem.product_id==product.id).first()

    if cartItem:
        cartItem.quantity+=1
        db.add(cartItem)
        db.commit()
        db.refresh(cartItem)
    else:
        cartItem=CartItem(cart_id=cart.id,product_id=product.id,quantity=1)
        db.add(cartItem)
        db.commit()
        db.refresh(cartItem)


    return {"product added to cart successfully":cartItem.cart_id,
            "product":{
                "product_id":product.id,
                "product_title":product.title,
                "product_image":product.image,
                "product_quantity":cartItem.quantity,
                "product_price":product.price*cartItem.quantity

            }}


@router.put("/cart/updatequantity/{product_id}",status_code=status.HTTP_201_CREATED)
async def update_cart_quantity(db:db_dependency,userdata:user_dependency,product_id:int= Path(gt=0)):
    userId=userdata["id"]
    if not userId:
        raise HTTPException(status_code=401,detail="Unauthorized error")
    cart=db.query(Cart).filter(Cart.user_id==userId).first()
    if not cart:
        raise HTTPException(status_code=400,detail="No cart found with user details")

    product=db.query(Product).filter(Product.id==product_id).first()
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    
    cartItem=db.query(CartItem).filter(CartItem.cart_id==cart.id,CartItem.product_id==product.id).first()

    if cartItem:
        if cartItem.quantity<1:
            db.delete(cartItem)
            db.commit()
            db.refresh(cartItem)
        else:
            cartItem.quantity-=1
            db.add(cartItem)
            db.commit()
            db.refresh(cartItem)
    else:
        raise HTTPException(status_code=400,detail="Product not found in cartItem")
    return {
        "product updated successfully":cartItem
    }



