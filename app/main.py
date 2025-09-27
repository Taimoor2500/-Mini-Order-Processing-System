from fastapi import FastAPI

app = FastAPI(title="Order Processing", version="1.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to my Order Processing System!"}
