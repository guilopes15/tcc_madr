from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr.database import get_session
from madr.models import Romancista, User
from madr.schemas import RomancistaPublic, RomancistaSchema
from madr.security import get_current_user

T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(get_session)]


router = APIRouter(prefix='/romancista', tags=['romancista'])


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=RomancistaPublic
)
def create_romancista(
    romancista: RomancistaSchema,
    user: T_CurrentUser,
    session: T_Session,
):
    db_romancista = session.scalar(
        select(Romancista).where(Romancista.nome == romancista.nome)
    )

    if db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Romancista ja costa no MADR',
        )

    db_romancista = Romancista(nome=romancista.nome)
    session.add(db_romancista)
    session.commit()
    session.refresh(db_romancista)

    return db_romancista
