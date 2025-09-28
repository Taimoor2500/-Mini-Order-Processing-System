from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.db.session import engine, Base, SessionLocal
from app.db.models import Order
from app.api import orders

app = FastAPI(title="Order Processing", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(orders.router)

add_pagination(app)

@app.get("/")
def read_root():
    return {"message": "Welcome to my Order Processing System!"}
