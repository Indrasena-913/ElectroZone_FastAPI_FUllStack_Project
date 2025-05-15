import enum
from fastapi import APIRouter, Body,HTTPException,Path, Query
from sqlalchemy import func
from starlette import status
from schema import QuantityUpdate
from database import db_dependency
from models import Product,Cart,CartItem,Order,OrderItem,OrderStatus
from .auth import user_dependency



router=APIRouter()


@router.post("/orders/create-order",status_code=status.HTTP_201_CREATED)
async def create_order(user:user_dependency,db:db_dependency):
    userId=user["id"]
    if not userId:
        raise HTTPException(status_code=401,detail="Unathorized")
    cart=db.query(Cart).filter(Cart.user_id==userId).first()
    if not cart:
            raise HTTPException(status_code=404,detail="cart not found")
    cartItems=db.query(CartItem).filter(CartItem.cart_id==cart.id).all()
    if not cartItems:
            raise HTTPException(status_code=404,detail="No products in cart")
    order=Order(user_id=userId)
    db.add(order)
    db.commit()
    db.refresh(order)
    print(cartItems)

    for item in cartItems:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue
        order_items=OrderItem(
               order_id=order.id,
               product_id=item.product.id,
               price=item.product.price*item.quantity,
               status=OrderStatus.PENDING 
          )
        db.add(order_items)
    for item in cartItems:
          db.delete(item)
    db.commit()
    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "order_items":order_items
    }

@router.get("/orders",status_code=status.HTTP_200_OK)
async def get_all_orders(user:user_dependency,db:db_dependency):
    userId=user["id"]
    if not userId:
        raise HTTPException(status_code=401,detail="Unathorized")
    orders=db.query(Order).filter(Order.user_id==userId).all()
    if not orders:
         raise HTTPException(status_code=404,detail="No orders found")
    orders_list=[]
    for order in orders:
        orderItems=db.query(OrderItem).filter(OrderItem.order_id==order.id).all()
        item_detail=[]
        for item in orderItems:
              product=db.query(Product).filter(Product.id==item.product_id).first()
              if product:
                   item_detail.append({
                        "product_id": product.id,
                    "title": product.title,
                    "price": item.price,
                    "status": item.status.value,
                        
                   })
        orders_list.append({
             "order_id":order.id,
             "created_at":order.created_at,
             "items":item_detail
        })
              
    return {
        "user_id": userId,
        "allorders":orders_list
    }
