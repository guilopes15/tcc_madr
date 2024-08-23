from http import HTTPStatus


def test_create_user(client):
    response = client.post(
        '/users/conta',
        json={
            'username': 'tEst UsErnAmE@!',
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
        '/users/conta',
        json={
            'username': 'test',
            'email': 'test2@test.com',
            'password': '123',
        },
    )

    response.status_code == HTTPStatus.BAD_REQUEST
    response.json() == {'detail': 'Username ja existi'}


def test_create_user_with_email_already_existent(client, user):
    response = client.post(
        '/users/conta',
        json={
            'username': 'test2',
            'email': 'test@test.com',
            'password': '123',
        },
    )

    response.status_code == HTTPStatus.BAD_REQUEST
    response.json() == {'detail': 'Email ja existi'}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/conta/{user.id}',
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


def test_update_user_sanitized(client, user, token):
    response = client.put(
        f'/users/conta/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'id': user.id,
            'username': 'TesT2!!!!!!',
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
        f'/users/conta/{other_user.id}',
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
    response.json() == {'detail': 'Sem permissao'}


def test_update_user_with_username_or_email_already_exists(
    client, token, user, other_user
):
    response = client.put(
        f'/users/conta/{user.id}',
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
    assert response.json() == {'detail': 'username ou email ja existi'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/conta/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    response.status_code == HTTPStatus.OK
    response.json() == {'message': 'Conta deletada com sucesso'}


def test_delete_other_user(client, token):
    response = client.delete(
        '/users/conta/3', headers={'Authorization': f'Bearer {token}'}
    )

    response.status_code == HTTPStatus.FORBIDDEN
    response.json() == {'detail': 'Sem permissao'}
