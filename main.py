from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

from sqlalchemy import create_engine, Integer, String, column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///./livros.db'

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

MEU_USUARIO = 'admin'
MINHA_SENHA = 'admin'

security = HTTPBasic()

def autenticar_meu_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, MEU_USUARIO)
    is_password_correct = secrets.compare_digest(credentials.password, MINHA_SENHA)
    
    if not (is_password_correct, is_username_correct):
        raise HTTPException(
            status_code=401,
            detail='Usuario ou senha incorretos.',
            headers={'WWW-Authenticate':'Basic'}
        )
        

meus_livros = dict()

class LivrosDB(Base):
    __tablename__ = "Livros"
    id_livro = column(Integer, primary_key = True, index = True)
    nome_livro = column(String, index = True)
    autor_livro = column(String, index = True)
    ano_livro = column(Integer)
    
Base.metadata.create_all(bind=engine)

class LivrosFormato(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

@app.get('/livros')
def get_livros(credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    if not meus_livros:
        return {'mensagem' : 'A livraria está vazia.'}
    else:
        return {'livros': meus_livros}
    
@app.post('/adicionar')
def post_livros(id_livro: int, livro : LivrosFormato, credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    if id_livro in meus_livros:
        raise HTTPException(status_code = 400, detail = 'Esse livro ja foi registrado.')
    else:
        meus_livros[id_livro] = livro.dict()
        return {'message' : 'Livro adicionado com sucesso'}
@app.put('/atualizar/{id_livro}')
def put_livros(id_livro: int, livro: LivrosFormato):
    meu_livro = meus_livros.get(id_livro)
    if id_livro not in meus_livros:
        raise HTTPException(status_code = 404, detail = 'O livro não foi encontrado.')
    else:
        meus_livros[id_livro] = livro.dict()
            
    return {'message': 'Livro atualizado com sucesso.'}

@app.delete('/deletar/{id_livro}')          
def delete_livros(id_livro: int):
    if id_livro not in meus_livros:
        raise HTTPException(status_code = 404, detail = 'O livro não foi encontrado.')
    else:
        del meus_livros[id_livro]
        return {'message': 'Seu livro foi deletado com sucesso.'}