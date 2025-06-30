from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.core import get_db
from app.crud.schools import SchoolCRUD
from app.schemas.schools import SchoolData, SchoolOut, SchoolUpdate, SchoolUpdateOut
from app.exceptions.school import SchoolNotFound

import logging

logger = logging.getLogger(__name__)

school_router = APIRouter(
    prefix='/schools', 
    tags=['school']
    )


@school_router.post('/', status_code=status.HTTP_201_CREATED, response_model=SchoolOut)
def add_school(db: Annotated[Session, Depends(get_db)], data: SchoolData):
    try:
        school = SchoolCRUD.create_school(db=db, data=data)
        return school
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'School name {data.name} is already used')
    except Exception as e:
        logger.exception(f'Unexcpeted error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@school_router.get('/', status_code=status.HTTP_200_OK, response_model=dict)
def get_school_id(db: Annotated[Session, Depends(get_db)], school_name: str):
    try:
        school = SchoolCRUD.get_school(db=db, name=school_name)
        return school
    except SchoolNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"School with name '{school_name} is not found'")
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@school_router.patch('/{school_id}', status_code=status.HTTP_200_OK, response_model=SchoolUpdateOut)
def update_school_data(db: Annotated[Session, Depends(get_db)], school_id: Annotated[int, Path()], data: SchoolUpdate):
    try:
        updated_school = SchoolCRUD.update_school_data(db=db, school_id=school_id, data=data)
        return updated_school
    except SchoolNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'School with id {school_id} is not found')
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'School with name {data.name} does not exist')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@school_router.delete('/{school_id}', status_code=status.HTTP_200_OK, response_model=bool)
def delete_school(db: Annotated[Session, Depends(get_db)], school_id: Annotated[int, Path()]):
    try:
        SchoolCRUD.delete_school(db=db, school_id=school_id)
        return {'detail': f'school with id {school_id} was deleted'}
    except SchoolNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'School with id: {school_id} is not found')
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)