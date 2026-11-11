from fastapi import FastAPI

from routes import system_admin

app = FastAPI(
    title="IT Asset Management System",
    description="IT Asset Management API",
    version="1.0.0"
)

app.include_router(system_admin.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to the IT Asset Management System"
    }