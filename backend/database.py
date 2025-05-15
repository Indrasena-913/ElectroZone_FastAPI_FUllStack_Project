from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base,Session

from dotenv import load_dotenv
load_dotenv()
import os


Database_URL=os.getenv("DATABASE_URL")

engine=create_engine(Database_URL)
SessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]