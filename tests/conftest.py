import random

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from madr.app import app
from madr.database import get_session
from madr.models import Livro, Romancista, User, table_registry
from madr.security import get_password_hash


class RomancistaFactory(factory.Factory):
    class Meta:
        model = Romancista

    nome = factory.Sequence(lambda n: f'nome={n}')


class LivroFactory(factory.Factory):
    class Meta:
        model = Livro

    ano = factory.LazyFunction(lambda: random.randint(1500, 2024))
    titulo = factory.Sequence(lambda n: f'titulo={n}')
    romancista_id = 1


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(session):
    password = '123'
    user = User(
        username='test',
        email='test@test.com',
        password=get_password_hash(password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password
    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = '321'
    user = User(
        username='test1',
        email='test1@test.com',
        password=get_password_hash(password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )
    return response.json()['access_token']


@pytest_asyncio.fixture
async def romancista(session):
    romancista = Romancista(nome='test')
    session.add(romancista)
    await session.commit()
    await session.refresh(romancista)
    return romancista


@pytest_asyncio.fixture
async def other_romancista(session):
    other_romancista = Romancista(nome='test1')
    session.add(other_romancista)
    await session.commit()
    await session.refresh(other_romancista)
    return other_romancista


@pytest_asyncio.fixture
async def livro(session, romancista):
    livro = Livro(
        ano=1999,
        titulo='o mundo assombrado pelos demônios',
        romancista_id=romancista.id,
    )
    session.add(livro)
    await session.commit()

    return livro


@pytest_asyncio.fixture
async def other_livro(session, romancista):
    livro = Livro(
        ano=1999, titulo='otherlivrotitulo', romancista_id=romancista.id
    )
    session.add(livro)
    await session.commit()

    return livro
