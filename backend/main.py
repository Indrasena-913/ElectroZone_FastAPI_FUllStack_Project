from fastapi import FastAPI
import models
from database import Base,engine
from routers import auth,products,cart,orders
from fastapi.middleware.cors import CORSMiddleware


app=FastAPI()

origins=["http://192.168.1.9:5500"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)



app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)

models.Base.metadata.create_all(bind=engine)