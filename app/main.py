from fastapi import FastAPI
from app.routes import file_names

app=FastAPI()

@app.get("/")
def landing_page():
    return{
        "message":"AI "
    }

@app.get("/health")
def health():
    return{
        "message":"ok"
    }
app.include_router(file_names.router)