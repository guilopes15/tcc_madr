# O que é o MADR?

Madr ou Meu Acervo Digital de Romances é uma **API** para gestão de livros. Este projeto surgiu como tcc do curso [FastZero](https://fastapidozero.dunossauro.com/#pre-requisitos), disponibilizado pelo [Dunossauro](https://github.com/dunossauro).

#### Observações iniciais

Neste projeto decidi utilizar a mesma estrutura do curso fastzero, por ser o meu primeiro projeto com o framework [FastAPI](https://fastapi.tiangolo.com/). 

#### Bibliotecas fora do escopo do curso

* Para sanitizar os nomes usei o **python-slugify**, esta biblioteca limpa os caracteres especiais, letras maiusculas, acentuação e etc.  

```bash
poetry add python-slugify
```

### Como utilizar?
Antes de tudo instale o [python](https://www.python.org/downloads/) e o [docker](https://docs.docker.com/engine/install/) na máquina.


É preciso também criar um arquivo **`.env`** na raiz do projeto(pasta onde fica o pyproject.toml) com as seguintes variaveis:

```plaintext
DATABASE_URL="postgresql+psycopg://app_user:app_password@localhost:5432/app_db"
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Depois execute:

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
```       
{
    'username': 'test@test.com', 
    'password': 'password'
}
```
* ***Refresh Token*** - *login required*

O token expira em 60 minutos, então faça um post no endpoint abaixo antes do tempo expirar, para permanecer utilizando a aplicação:
>POST /auth/refresh_token

#### Users, Livro e Romancista
Utilize o **redoc** para mais informações sobre todas as rotas disponíveis.

>localhost:8000/redoc
