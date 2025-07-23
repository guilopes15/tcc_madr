import pytest
from sqlalchemy import select

from madr.models import Livro, Romancista, User


@pytest.mark.asyncio
async def test_create_user_on_db(session):
    user = User(username='gui', email='test@test.com', password='123')
    session.add(user)
    await session.commit()
    result = await session.scalar(
        select(User).where(User.username == user.username)
    )
    assert result


@pytest.mark.asyncio
async def test_create_romancista_on_db(session):
    romancista = Romancista(nome='test')
    session.add(romancista)
    await session.commit()
    result = await session.scalar(
        select(Romancista).where(Romancista.nome == romancista.nome)
    )
    assert result


@pytest.mark.asyncio
async def teste_create_livro_on_db(session, romancista):
    livro = Livro(
        ano=1999,
        titulo='o mundo assombrado pelos demônios',
        romancista_id=romancista.id,
    )
    session.add(livro)
    await session.commit()
    result = await session.scalar(select(Livro).where(Livro.ano == livro.ano))
    assert result
