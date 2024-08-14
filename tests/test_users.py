from http import HTTPStatus

import pytest
from fastapi import HTTPException
from jwt import decode, encode

from madr.security import create_access_token, get_current_user
from madr.settings import Settings


def test_create_user(client):
    response = client.post(
        '/conta',
        json={
            'username': 'tEst UsErnAmE @!',
            'email': 'test@test.com',
            'password': 'password',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'test username',
        'email': 'test@test.com',
    }


def test_create_user_with_username_already_existent(client, user):
    response = client.post(
        '/conta',
        json={
            'username': 'test',
            'email': 'test2@test.com',
            'password': '123',
        },
    )

    response.status_code == HTTPStatus.BAD_REQUEST
    response.json() == {'detail': 'Username alread exists'}


def test_create_user_with_email_already_existent(client, user):
    response = client.post(
        '/conta',
        json={
            'username': 'test2',
            'email': 'test@test.com',
            'password': '123',
        },
    )

    response.status_code == HTTPStatus.BAD_REQUEST
    response.json() == {'detail': 'Email alread exists'}


def test_update_user(client, user, token):
    response = client.put(
        f'/conta/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'id': user.id,
            'username': 'test2',
            'email': 'test2@test.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'test2',
        'email': 'test2@test.com',
    }


def test_update_user_with_invalid_id(client, token, other_user):
    response = client.put(
        f'/conta/{other_user.id}',
        headers={
            'Authorization': f'Bearer {token}',
        },
        json={
            'username': 'test3',
            'email': 'test@test.com',
            'password': '123',
        },
    )

    response.status_code == HTTPStatus.FORBIDDEN
    response.json() == {'detail': 'Not enough permission'}


def test_update_user_with_username_or_email_already_exists(
    client, token, user, other_user
):
    response = client.put(
        f'/conta/{user.id}',
        headers={
            'Authorization': f'Bearer {token}',
        },
        json={
            'username': other_user.username,
            'email': other_user.email,
            'password': other_user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already exists'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/conta/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    response.status_code == HTTPStatus.OK
    response.json() == {'message': 'Conta deletada com sucesso'}


def test_delete_other_user_(client, token):
    response = client.delete(
        '/conta/3', headers={'Authorization': f'Bearer {token}'}
    )

    response.status_code == HTTPStatus.FORBIDDEN
    response.json() == {'detail': 'Not enough permission'}


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_token_with_wrong_password(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': 'test'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_with_wrong_email(client, user):
    response = client.post(
        '/token',
        data={'username': 'wrong@wrong.com', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_resfresh_token(client, token):
    response = client.post(
        '/refresh_token',
        headers={
            'Authorization': f'Bearer {token}',
        },
    )
    data = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_get_current_user_not_found(token, session):
    data = {'sub': 'None@none.com'}
    token_override = encode(
        data, Settings().SECRET_KEY, algorithm=Settings().ALGORITHM
    )

    with pytest.raises(HTTPException) as ex:
        get_current_user(session, token_override)

    assert ex.value.status_code == HTTPStatus.UNAUTHORIZED
    assert ex.value.detail == 'Could not validate credentials'


def test_get_current_user_without_sub(session):
    data = {}
    token_override = encode(
        data, Settings().SECRET_KEY, algorithm=Settings().ALGORITHM
    )

    with pytest.raises(HTTPException) as ex:
        get_current_user(session, token_override)

    assert ex.value.status_code == HTTPStatus.UNAUTHORIZED
    assert ex.value.detail == 'Could not validate credentials'


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
        '/conta/1',
        headers={'Authorization': 'Bearer token-invalido'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
