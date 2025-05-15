from fastapi import FastAPI
import models
from database import Base,engine
from routers import auth,products,cart


app=FastAPI()
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)

models.Base.metadata.create_all(bind=engine)