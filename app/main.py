from fastapi import FastAPI

from app.api.v1.endpoints.auth import auth_router
from app.api.v1.endpoints.users import users_router
from app.api.v1.endpoints.school import school_router
from app.api.v1.endpoints.principal import principal_router
from app.api.v1.endpoints.groups import groups_router
from app.api.v1.endpoints.subjects import subject_router
from app.api.v1.endpoints.homeworks import homeworks_router
from app.api.v1.endpoints.schedules import schedules_router
from app.api.v1.endpoints.teacher import teacher_router
from app.logging.logger import *

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(school_router)
app.include_router(principal_router)
app.include_router(groups_router)
app.include_router(subject_router)
app.include_router(homeworks_router)
app.include_router(schedules_router)
app.include_router(teacher_router)