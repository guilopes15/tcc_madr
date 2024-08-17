from http import HTTPStatus

from tests.conftest import LivroFactory


def test_create_livro(client, token):
    response = client.post(
        '/livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1999,
            'titulo': 'café da manhã dos campeões',
            'romancista_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'ano': 1999,
        'titulo': 'cafe da manha dos campeoes',
        'romancista_id': 1,
    }


def test_create_livro_already_existent(client, token, livro):
    response = client.post(
        '/livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1999,
            'titulo': 'o mundo assombrado pelos demônios',
            'romancista_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'livro ja consta no MADR'}


def test_delete_livro(client, token, livro):
    response = client.delete(
        f'/livro/{livro.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Livro deletado no MADR'}


def test_delete_livro_not_found(client, token):
    response = client.delete(
        '/livro/99', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro nao consta no MADR'}


def test_path_livro(client, token, livro):
    response = client.patch(
        f'/livro/{livro.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1958,
            'titulo': 'testnomelivro',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'ano': 1958,
        'titulo': 'testnomelivro',
        'romancista_id': 1,
    }


def test_path_livro_sanitized(client, token, livro):
    response = client.patch(
        f'/livro/{livro.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1958,
            'titulo': 'tEstnOmElIvrO@@!!&&',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'ano': 1958,
        'titulo': 'testnomelivro',
        'romancista_id': 1,
    }


def test_path_livro_not_found(client, token, livro):
    response = client.patch(
        '/livro/99',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1958,
            'titulo': 'testnomelivro',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro nao consta no MADR'}


def test_path_livro_with_titulo_already_exist(
    client, token, livro, other_livro
):
    response = client.patch(
        f'/livro/{livro.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1958,
            'titulo': other_livro.titulo,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Este titulo ja consta no MADR'}


def test_get_livro_by_id(client, livro):
    response = client.get(f'/livro/{livro.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'ano': 1999,
        'titulo': 'o mundo assombrado pelos demônios',
        'romancista_id': 1,
    }


def test_get_livro_by_id_not_found(client, livro):
    response = client.get('/livro/99')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro nao consta no MADR'}


def test_list_livro(client, livro):
    response = client.get('/livro/?ano=9&titulo=o')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'livros': [
            {
                'id': 1,
                'ano': 1999,
                'titulo': 'o mundo assombrado pelos demônios',
                'romancista_id': 1,
            }
        ]
    }


def test_list_livro_empty(client, livro):
    response = client.get('/livro/?ano=8')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'livros': []}


def test_list_livro_should_return_3_livros(session, client, token):
    expected_livros = 3
    session.bulk_save_objects(LivroFactory.create_batch(3))
    session.commit()
    response = client.get(
        '/livro', headers={'Authorization': f'Bearer {token}'}
    )
    assert len(response.json()['livros']) == expected_livros


def test_list_livro_offset(session, client, token):
    session.bulk_save_objects(LivroFactory.create_batch(5))
    session.commit()
    response = client.get(
        '/livro/?offset=1', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.json()['livros'][0]['id'] != 1


def test_list_livro_limit_20(session, client, token):
    expected_livros = 20
    session.bulk_save_objects(LivroFactory.create_batch(21))
    session.commit()
    response = client.get(
        '/livro', headers={'Authorization': f'Bearer {token}'}
    )
    assert len(response.json()['livros']) == expected_livros
