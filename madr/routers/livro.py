from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from madr.database import get_session
from madr.models import Livro, User
from madr.schemas import (
    LivroList,
    LivroPublic,
    LivroSchema,
    LivroUpdate,
    Message,
)
from madr.security import get_current_user

router = APIRouter(prefix='/livro', tags=['livro'])
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(get_session)]


@router.post('/', status_code=HTTPStatus.OK, response_model=LivroPublic)
def create_livro(livro: LivroSchema, session: T_Session, user: T_CurrentUser):
    db_livro = session.scalar(
        select(Livro).where(Livro.titulo == livro.titulo)
    )
    if db_livro:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Livro ja consta no MADR'
        )

    db_livro = Livro(
        ano=livro.ano,
        titulo=slugify(livro.titulo, separator=' '),
        romancista_id=livro.romancista_id,
    )

    session.add(db_livro)
    session.commit()
    session.refresh(db_livro)

    return db_livro


@router.delete(
    '/{livro_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_livro(livro_id: int, session: T_Session, user: T_CurrentUser):
    db_livro = session.scalar(select(Livro).where(Livro.id == livro_id))

    if not db_livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Livro nao consta no MADR'
        )

    session.delete(db_livro)
    session.commit()

    return {'message': 'Livro deletado no MADR'}


@router.patch(
    '/{livro_id}', status_code=HTTPStatus.OK, response_model=LivroPublic
)
def patch_livro(
    livro_id: int, session: T_Session, user: T_CurrentUser, livro: LivroUpdate
):
    db_livro = session.scalar(select(Livro).where(Livro.id == livro_id))

    if not db_livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Livro nao consta no MADR'
        )

    try:
        for key, value in livro.model_dump(exclude_unset=True).items():
            setattr(db_livro, key, value)

        db_livro.titulo = slugify(db_livro.titulo, separator=' ')
        session.add(db_livro)
        session.commit()
        session.refresh(db_livro)

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Este titulo ja consta no MADR',
        )

    return db_livro


@router.get(
    '/{livro_id}', status_code=HTTPStatus.OK, response_model=LivroPublic
)
def get_livro_by_id(livro_id: int, session: T_Session):
    db_livro = session.scalar(select(Livro).where(Livro.id == livro_id))

    if not db_livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Livro nao consta no MADR'
        )

    return db_livro


@router.get('/', status_code=HTTPStatus.OK, response_model=LivroList)
def list_livro(
    session: T_Session,
    ano: int | None = None,
    titulo: str | None = None,
    offset: int | None = None,
    limit: int | None = 20,
):
    query = select(Livro)

    if ano:
        query = query.where(Livro.ano == ano)

    if titulo:
        query = query.filter(Livro.titulo.contains(titulo))

    list_livros = session.scalars(query.offset(offset).limit(limit)).all()

    return {'livros': list_livros}
