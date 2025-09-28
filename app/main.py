from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.db.session import engine, Base, SessionLocal
from app.db.models import Order
from app.api import orders
from app.utils.rate_limiter import limiter

app = FastAPI(title="Order Processing", version="1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
