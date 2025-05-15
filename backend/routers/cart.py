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

@router.put("/cart/updatequantity/{product_id}", status_code=status.HTTP_200_OK)
async def update_cart_quantity(db: db_dependency,userdata: user_dependency,product_id: int = Path(gt=0)):
    user_id = userdata["id"]
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized error")

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=400, detail="No cart found for this user")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Product not found in cart")

    if cart_item.quantity <= 1:
        db.delete(cart_item)
        db.commit()
        return {"message": "Product removed from cart"}
    else:
        cart_item.quantity -= 1
        db.commit()
        db.refresh(cart_item)
        return {
            "message": "Product quantity updated",
            "cart_item": {
                "product_id": product.id,
                "product_title": product.title,
                "product_image":product.image,
                "quantity": cart_item.quantity,
                "total_price": product.price * cart_item.quantity
            }
        }



@router.get("/cart", status_code=status.HTTP_200_OK)
async def get_user_cart(db: db_dependency,userdata: user_dependency):
    user_id = userdata["id"]
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized error")

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

    if not cart_items:
        return {"message": "Cart is empty"}

    response = []
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        response.append({
            "product_id": product.id,
            "title": product.title,
            "image": product.image,
            "price_per_unit": product.price,
            "quantity": item.quantity,
            "total_price": product.price * item.quantity
        })

    return {
        "cart_id": cart.id,
        "total_items": len(cart_items),
        "items": response
    }




@router.delete("/cart/clear", status_code=status.HTTP_200_OK)
async def clear_cart(
    db: db_dependency,
    userdata: user_dependency
):
    user_id = userdata["id"]
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized error")

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    deleted = db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()

    return {"message": f"{deleted} item(s) removed from cart"}
