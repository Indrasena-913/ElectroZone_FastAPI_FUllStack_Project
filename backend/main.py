from fastapi import FastAPI
import models
from database import Base,engine
from routers import auth,products,cart,orders
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum


app=FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

handler = Mangum(app)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)

models.Base.metadata.create_all(bind=engine)