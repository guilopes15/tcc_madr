from sqlalchemy import select

from madr.models import Livro, Romancista, User


def test_create_user_on_db(session):
    user = User(username='gui', email='test@test.com', password='123')
    session.add(user)
    session.commit()
    result = session.scalar(select(User).where(User.username == user.username))
    assert result


def test_create_romancista_on_db(session):
    romancista = Romancista(nome='test')
    session.add(romancista)
    session.commit()
    result = session.scalar(
        select(Romancista).where(Romancista.nome == romancista.nome)
    )
    assert result


def teste_create_livro_on_db(session):
    livro = Livro(
        ano=1999, titulo='o mundo assombrado pelos demônios', romancista_id=1
    )
    session.add(livro)
    session.commit()
    result = session.scalar(select(Livro).where(Livro.ano == livro.ano))
    assert result
