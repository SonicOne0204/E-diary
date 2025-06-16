from fastapi import FastAPI
from app.api.v1.endpoints.auth import auth_router
from app.api.v1.endpoints.users import users_router
from app.api.v1.endpoints.school import school_router
app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(school_router)
