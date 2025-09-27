from fastapi import FastAPI

from app.db.session import engine, Base, SessionLocal
from app.db.models import Order

app = FastAPI(title="Order Processing", version="1.0")

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to my Order Processing System!"}
