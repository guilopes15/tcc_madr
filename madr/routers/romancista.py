from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database import get_session
from madr.models import Romancista, User
from madr.schemas import (
    Message,
    RomancistaList,
    RomancistaPublic,
    RomancistaSchema,
    RomancistaUpdate,
)
from madr.security import get_current_user

T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[AsyncSession, Depends(get_session)]


router = APIRouter(prefix='/romancista', tags=['romancista'])


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=RomancistaPublic
)
async def create_romancista(
    romancista: RomancistaSchema,
    user: T_CurrentUser,
    session: T_Session,
):
    db_romancista = await session.scalar(
        select(Romancista).where(Romancista.nome == romancista.nome)
    )

    if db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Romancista ja costa no MADR',
        )

    db_romancista = Romancista(nome=slugify(romancista.nome, separator=' '))
    session.add(db_romancista)
    await session.commit()
    await session.refresh(db_romancista)

    return db_romancista


@router.delete(
    '/{romancista_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
async def delete_romancista(
    romancista_id: int, user: T_CurrentUser, session: T_Session
):
    romancista = await session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista nao consta no MADR',
        )

    await session.delete(romancista)
    await session.commit()

    return {'message': 'Romancista deletado(a) do MADR'}


@router.patch(
    '/{romancista_id}',
    status_code=HTTPStatus.OK,
    response_model=RomancistaPublic,
)
async def patch_romancista(
    romancista_id: int,
    user: T_CurrentUser,
    session: T_Session,
    romancista: RomancistaUpdate,
):
    db_romancista = await session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista nao consta no MADR',
        )

    try:
        for key, value in romancista.model_dump(exclude_unset=True).items():
            setattr(db_romancista, key, value)

        db_romancista.nome = slugify(db_romancista.nome, separator=' ')
        session.add(db_romancista)
        await session.commit()
        await session.refresh(db_romancista)

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Este nome ja consta no MADR',
        )

    return db_romancista


@router.get(
    '/{romancista_id}',
    status_code=HTTPStatus.OK,
    response_model=RomancistaPublic,
)
async def get_romancista(romancista_id: int, session: T_Session):
    db_romancista = await session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )
    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista nao consta no MADR',
        )

    return db_romancista


@router.get('/', status_code=HTTPStatus.OK, response_model=RomancistaList)
async def list_romancista(
    session: T_Session,
    nome: str | None = None,
    offset: int | None = None,
    limit: int | None = 20,
):
    query = select(Romancista)

    if nome:
        query = query.filter(Romancista.nome.contains(nome))

    list_romancistas = await session.scalars(query.offset(offset).limit(limit))

    return {'romancistas': list_romancistas.all()}
