from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from madr.database import get_session
from madr.models import User
from madr.schemas import Message, UserPublic, UserSchema
from madr.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/conta', status_code=HTTPStatus.CREATED, response_model=UserPublic
)
def create_user(user: UserSchema, session: T_Session):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username alread exists',
            )

        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email alread exists',
            )

    db_user = User(
        username=slugify(user.username, separator=' '),
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put('/conta/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permission'
        )

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        session.commit()
        session.refresh(current_user)

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='username or email already exists',
        )

    return current_user


@router.delete('/conta/{user_id}', response_model=Message)
def delete_user(user_id: int, session: T_Session, current_user: T_CurrentUser):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permission'
        )
    session.delete(current_user)
    session.commit()
    return {'message': 'Conta deletada com sucesso'}
