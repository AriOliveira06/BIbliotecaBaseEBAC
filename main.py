from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

meus_livros = dict()

class LivrosFormato(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

@app.get('/livros')
def get_livros():
    if not meus_livros:
        return {'mensagem' : 'A livraria está vazia.'}
    else:
        return {'livros': meus_livros}
    
@app.post('/adicionar')
def post_livros(id_livro: int, livro : LivrosFormato):
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
        meu_livro[id_livro] = livro.dict()
            
    return {'message': 'Livro atualizado com sucesso.'}

@app.delete('/deletar/{id_livro}')          
def delete_livros(id_livro: int):
    if id_livro not in meus_livros:
        raise HTTPException(status_code = 404, detail = 'O livro não foi encontrado.')
    else:
        del meus_livros[id_livro]
        return {'message': 'Seu livro foi deletado com sucesso.'}