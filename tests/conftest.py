import random

import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
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
    with PostgresContainer('postgres:16', driver='psycopg2') as postgres:
        engine = create_engine(postgres.get_connection_url())
        with engine.begin():
            yield engine


@pytest.fixture
def session(engine):
    table_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def user(session):
    password = '123'
    user = User(
        username='test',
        email='test@test.com',
        password=get_password_hash(password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    user.clean_password = password
    return user


@pytest.fixture
def other_user(session):
    password = '321'
    user = User(
        username='test1',
        email='test1@test.com',
        password=get_password_hash(password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)
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


@pytest.fixture
def romancista(session):
    romancista = Romancista(nome='test')
    session.add(romancista)
    session.commit()
    session.refresh(romancista)
    return romancista


@pytest.fixture
def other_romancista(session):
    other_romancista = Romancista(nome='test1')
    session.add(other_romancista)
    session.commit()
    session.refresh(other_romancista)
    return other_romancista


@pytest.fixture
def livro(session, romancista):
    livro = Livro(
        ano=1999,
        titulo='o mundo assombrado pelos demônios',
        romancista_id=romancista.id,
    )
    session.add(livro)
    session.commit()

    return livro


@pytest.fixture
def other_livro(session, romancista):
    livro = Livro(
        ano=1999, titulo='otherlivrotitulo', romancista_id=romancista.id
    )
    session.add(livro)
    session.commit()

    return livro
