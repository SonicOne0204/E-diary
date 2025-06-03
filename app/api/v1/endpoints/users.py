from fastapi import APIRouter, Path, status, HTTPException
from crud.users import delete_user, get_user_id
from typing import Annotated

users_router = APIRouter(
    prefix='/users',
    tags=['users']
)

@users_router.get('/get-id', status_code=status.HTTP_202_ACCEPTED)
def get_id(username: str):
    return get_user_id(username=username)

@users_router.delete('/delete/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(user_id: Annotated[int, Path()]):
    delete_user(user_id=user_id)