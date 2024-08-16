from fastapi import FastAPI

from madr.routers import auth, livro, romancista, users

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(romancista.router)
app.include_router(livro.router)


@app.get('/')
def read_root():
    return {'message': 'test'}
