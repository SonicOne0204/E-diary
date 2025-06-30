from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.core import get_db
from app.crud.subjects import SubjectCRUD
from app.schemas.subjects import SubjectData, SubjectDataOut, SubjectUpdate, SubjectUpdateOut
from app.exceptions.subject import SubjectNotFound

import logging

logger = logging.getLogger(__name__)

subject_router = APIRouter(
    prefix='/subjects', 
    tags=['subject']
    )


@subject_router.post('/', status_code=status.HTTP_201_CREATED, response_model=SubjectDataOut)
def add_subject(db: Annotated[Session, Depends(get_db)], data: SubjectData):
    try:
        subject = SubjectCRUD.create_subject(db=db, data=data)
        return subject
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'subject name {data.name} is already used')
    except Exception as e:
        logger.exception(f'Unexcpeted error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@subject_router.get('/', status_code=status.HTTP_200_OK, response_model=SubjectDataOut)
def get_subject(db: Annotated[Session, Depends(get_db)], subject_name: str):
    try:
        subject = SubjectCRUD.get_subject(db=db, name=subject_name)
        return subject
    except SubjectNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"subject with name '{subject_name} is not found'")
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@subject_router.patch('/{subject_id}', status_code=status.HTTP_200_OK, response_model=SubjectUpdateOut)
def update_subject_data(db: Annotated[Session, Depends(get_db)], subject_id: Annotated[int, Path()], data: SubjectUpdate):
    try:
        updated_subject = SubjectCRUD.update_subject_data(db=db, subject_id=subject_id, data=data)
        return updated_subject
    except SubjectNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'subject with id {subject_id} is not found')
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'subject with name {data.name} does not exist')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@subject_router.delete('/{subject_id}', status_code=status.HTTP_200_OK, response_model=bool)
def delete_subject(db: Annotated[Session, Depends(get_db)], subject_id: Annotated[int, Path()]):
    try:
        SubjectCRUD.delete_subject(db=db, subject_id=subject_id)
        return True
    except SubjectNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'subject with id: {subject_id} is not found')
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)