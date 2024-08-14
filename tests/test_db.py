from sqlalchemy import select

from madr.models import User


def test_create_user_on_db(session):
    user = User(username='gui', email='test@test.com', password='123')
    session.add(user)
    session.commit()
    result = session.scalar(select(User).where(User.username == user.username))
    assert result
