from http import HTTPStatus


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_token_with_wrong_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'test'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_with_wrong_email(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'wrong@wrong.com', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_resfresh_token(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={
            'Authorization': f'Bearer {token}',
        },
    )
    data = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'
