from fastapi import FastAPI

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
