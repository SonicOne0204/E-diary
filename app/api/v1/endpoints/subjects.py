from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.core import get_db
from app.crud.subjects import SubjectCRUD
from app.schemas.subjects import SubjectData, SubjectDataOut, SubjectUpdate, SubjectUpdateOut
from app.exceptions.basic import NotFound, NotAllowed
from app.db.models.users import User
from app.services.auth import get_current_user
from app.dependecies.auth import check_role
from app.schemas.auth import UserTypes
from app.db.models.subjects import Subject


import logging

logger = logging.getLogger(__name__)

subject_router = APIRouter(
    prefix='/subjects', 
    tags=['subject']
    )


@subject_router.post('/', status_code=status.HTTP_201_CREATED, response_model=SubjectDataOut, dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))])
def add_subject(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], data: SubjectData) -> Subject:
    try:
        subject = SubjectCRUD.create_subject(db=db, user=user, data=data)
        return subject
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'subject name {data.name} is already used')
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@subject_router.get('/{subject_id}', response_model=SubjectDataOut, dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))])
def get_subject(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], subject_id: str) -> Subject:
    try:
        subject = SubjectCRUD.get_subject_id(db=db, user=user,subject_id=subject_id)
        return subject
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"subject is not found'")
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@subject_router.patch('/{subject_id}', response_model=SubjectUpdateOut, dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))])
def update_subject_data(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], subject_id: Annotated[int, Path()], data: SubjectUpdate) -> Subject:
    try:
        updated_subject = SubjectCRUD.update_subject_data(db=db, user=user,subject_id=subject_id, data=data)
        return updated_subject
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'subject with id {subject_id} is not found')
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'subject with name {data.name} does not exist')
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@subject_router.delete('/{subject_id}', dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))])
def delete_subject(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], subject_id: Annotated[int, Path()]) -> Subject:
    try:
        SubjectCRUD.delete_subject(db=db, user=user,subject_id=subject_id)
        logger.debug(f'Subject with id {subject_id} was deleted')
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'subject with id: {subject_id} is not found')
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@subject_router.get('/', response_model=list[SubjectDataOut], dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal, UserTypes.student, UserTypes.teacher]))])
def get_subjects(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)] ,school_id: int , name: str | None = None) -> list[Subject]:
    try:
        subjects: Subject = SubjectCRUD.get_subjects(db=db, school_id=school_id, user=user ,name=name)
        return subjects
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)