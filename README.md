# O que é o MADR?

Madr ou Meu Acervo Digital de Romances é uma **API** para gestao de livros. Este projeto surgiu como tcc do curso [FastZero](https://fastapidozero.dunossauro.com/#pre-requisitos), disponibilizado pelo [Dunossauro](https://github.com/dunossauro).

#### Observações iniciais

Neste projeto decidi utilizar a mesma estrutura do curso fastzero, por ser o meu primeiro projeto com o framework [FastAPI](https://fastapi.tiangolo.com/). Também pensei em usar o [FastAPIUsers](https://fastapi-users.github.io/fastapi-users/latest/) mas achei que nao daria tempo de aprender até o fim de agosto.

#### Bibliotecas fora do escopo do curso
 
 * Utilizei o **psycopg2** porque tive um problema com  o "psycopg[binary]" ao aplicar a migração dentro do conteiner do flyio. 
<br>
    
    TypeError: cannot use a string pattern on a bytes-like object.

O erro foi resolvido ao utilizar o psycopg2. Obs: quem souber o por que do erro e quiser abrir uma issue, desde ja agradeço.

```bash
poetry add psycopg2-binary
```

 * Para sanitizar os nomes usei o **python-slugify**, esta biblioteca limpa os caracteres especiais, letras maiusculas e os acentos.  

```bash
poetry add python-slugify
```

### Como utilizar?
Antes de tudo instale o [python](https://www.python.org/downloads/) e o [docker](https://docs.docker.com/engine/install/) na máquina.


É preciso também criar um arquivo **`.env`** na raiz do projeto com as seguintes variaveis:

```plaintext
DATABASE_URL="postgresql+psycopg2://app_user:app_password@localhost:5432/app_db"
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```



Com o terminal aberto, navegue até a pasta raiz (pasta onde fica o pyproject.toml) e execute:

```bash
docker compose up --build
```
Com isso a **API** já esta rodando localmente dentro de um conteiner docker.


#### Swagger
Utilize o swagger para testar todas as rotas e verificar os schemas.

Acesse: 
>localhost:8000/docs



#### Login
Alguns endpoints é necessario estar logado para acessar, e este projeto não possui uma tela de login, então utilize o swagger para isso.
Os endpoints com *login required* é necessario passar informações no header da requisição.
```
hearders={'Authorization': 'Bearer {token}'}
```

### Rotas

#### Auth
* ***Token JWT***

É preciso ter o token jwt do tipo Bearer para realizar a autentificação, então faça um post no seguinte endpoint:
> POST /auth/token
```json       
{
    'username': 'test@test.com', 
    'password': 'password'
}
```
* ***Refresh Token*** - *login required*

O token expira em 60 minutos, então faça um post no endpoint abaixo antes do tempo expirar, para permanecer utilizando a aplicação:
>POST /auth/refresh_token'

#### Users
* ***Criar usuario***
> POST /users/conta
```json
{
    'username': 'testusername',
    'email': 'test@test.com',
    'password': 'password'
}
```
* ***Deletar usuario*** - *login required*
> DELETE /users/conta/`{user.id}`

* ***Atualizar usuario*** - *login required*
> UPDATE /users/conta/`{user.id}`
```json
{           
    'id': 1,
    'username': 'test2',
    'email': 'test2@test.com',
    'password': 'password'
}
```
#### Romancista

* ***Criar Romancista*** - *login required*
> POST /romancista
```json
{
    'nome': 'test'
}
```

* ***Deletar Romancista*** - *login required*
> DELETE /romancista/`{romancista.id}`

* ***Atualizar romancista*** - *login required*
> PATCH /romancista/`{romancista.id}`
```json
{
    'nome': 'testtest'
}
```


* ***Listar Romancista por id***
> GET /romancista/`{romancista.id}`


* ***Listar Romancista por queryparam***
> GET /romancista/?nome=t


#### Livro

* ***Criar livro*** - *login required*
> POST /livro
```json
{
    'ano': 1999,
    'titulo': 'café da manhã dos campeões',
    'romancista_id': 1      
}
```
* ***Deletar livro*** - *login required*
> DELETE /livro/`{livro.id}`
* ***Atualizar livro*** - *login required*
> PATCH /livro/`{livro.id}`
```json
{
    'ano': 1958,
    'titulo': 'testnomelivro'
}
```
* ***Listar livro por id***
>GET /livro/`{livro.id}`

* ***Listar livro por queryparam***
>GET /livro/?ano=1999&titulo=cafe
