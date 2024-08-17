from http import HTTPStatus

from tests.conftest import RomancistaFactory


def test_create_romancista(client, token):
    response = client.post(
        '/romancista',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'tEst2#!'},
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


def test_delete_romancista(client, token, romancista):
    response = client.delete(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Romancista deletado(a) do MADR'}


def test_delete_romacista_not_found(client, token, romancista):
    response = client.delete(
        '/romancista/99',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista nao consta no MADR'}


def test_patch_romancista(client, token, romancista):
    response = client.patch(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'testtest'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'nome': 'testtest'}


def test_patch_romancista_sanitized(client, token, romancista):
    response = client.patch(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'tEsttEst**&&'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'nome': 'testtest'}


def test_patch_romancista_not_found(client, token, romancista):
    response = client.patch(
        '/romancista/99',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'testtest'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista nao consta no MADR'}


def test_patch_romancista_with_nome_already_exist(
    client, token, romancista, other_romancista
):
    response = client.patch(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': other_romancista.nome},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Este nome ja consta no MADR'}


def test_get_romancista(client, romancista):
    response = client.get(f'/romancista/{romancista.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'nome': 'test'}


def test_get_romancista_not_found(client, romancista):
    response = client.get('/romancista/99')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista nao consta no MADR'}


def test_list_romancista(client, romancista):
    response = client.get('/romancista/?nome=t')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'romancistas': [{'id': 1, 'nome': 'test'}]}


def test_list_romancista_should_return_empty(client, romancista):
    response = client.get('/romancista/?nome=w')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'romancistas': []}


def test_list_romancista_should_return_3_romancistas(session, client, token):
    expected_romancistas = 3
    session.bulk_save_objects(RomancistaFactory.create_batch(3))
    session.commit()
    response = client.get(
        '/romancista', headers={'Authorization': f'Bearer {token}'}
    )
    assert len(response.json()['romancistas']) == expected_romancistas


def test_list_romancista_offset(session, client, token):
    session.bulk_save_objects(RomancistaFactory.create_batch(5))
    session.commit()
    response = client.get(
        '/romancista/?offset=1', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.json()['romancistas'][0]['id'] != 1


def test_list_romancista_limit_20(session, client, token):
    expected_romancistas = 20
    session.bulk_save_objects(RomancistaFactory.create_batch(21))
    session.commit()
    response = client.get(
        '/romancista', headers={'Authorization': f'Bearer {token}'}
    )
    assert len(response.json()['romancistas']) == expected_romancistas
