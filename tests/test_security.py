from http import HTTPStatus

import pytest
from fastapi import HTTPException
from jwt import decode, encode

from madr.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from madr.settings import Settings


def test_password_checker():
    password_hash = get_password_hash('test')
    assert verify_password('test', password_hash)


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)
    result = decode(
        token, Settings().SECRET_KEY, algorithms=[Settings().ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert result['exp']


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/conta/1',
        headers={'Authorization': 'Bearer token-invalido'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_not_found(session):
    data = {'sub': 'None@none.com'}
    token = encode(data, Settings().SECRET_KEY, algorithm=Settings().ALGORITHM)

    with pytest.raises(HTTPException) as ex:
        get_current_user(session, token)

    assert ex.value.status_code == HTTPStatus.UNAUTHORIZED
    assert ex.value.detail == 'Could not validate credentials'


def test_get_current_user_without_sub(session):
    data = {}
    token = encode(data, Settings().SECRET_KEY, algorithm=Settings().ALGORITHM)

    with pytest.raises(HTTPException) as ex:
        get_current_user(session, token)

    assert ex.value.status_code == HTTPStatus.UNAUTHORIZED
    assert ex.value.detail == 'Could not validate credentials'
