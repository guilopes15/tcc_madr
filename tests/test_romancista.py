from http import HTTPStatus


def test_create_romancista(client, token):
    response = client.post(
        '/romancista',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'test2'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'id': 1, 'nome': 'test2'}


def test_create_romancista_with_romancista(client, token, romancista):
    response = client.post(
        '/romancista',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'test'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Romancista ja costa no MADR'}
