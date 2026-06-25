from fastapi import FastAPI, HTTPException

app = FastAPI()

meus_livros = dict()

@app.get('/livros')
def get_livros():
    if not meus_livros:
        return {'mensagem' : 'A livraria está vazia.'}
    else:
        return {'livros': meus_livros}
    
@app.post('/adicionar')
def post_livros(id_livro: int, nome_livro: str, autor_livro: str, ano_livro: int):
    if id_livro in meus_livros:
        raise HTTPException(status_code = 400, detail = 'Esse livro ja foi registrado.')
    else:
        meus_livros[id_livro] = {'nome_livro': nome_livro, 'autor_livro': autor_livro, 'ano_livro': ano_livro}
        return {'message' : 'Livro adicionado com sucesso'}
@app.put('/atualizar/{id_livro}')
def put_livros(id_livro: int, nome_livro: str, autor_livro: str, ano_livro: int):
    meu_livro = meus_livros.get(id_livro)
    if id_livro not in meus_livros:
        raise HTTPException(status_code = 404, detail = 'O livro não foi encontrado.')
    else:
        if nome_livro:
            meus_livros[id_livro]['nome_livro'] = nome_livro
        if autor_livro:
            meus_livros[id_livro]['autor_livro'] = autor_livro
        if ano_livro:
            meus_livros[id_livro]['ano_livro'] = ano_livro
            
    return {'message': 'Livro atualizado com sucesso.'}

@app.delete('/deletar/{id_livro}')
def delete_livros(id_livro: int):
    if id_livro not in meus_livros:
        raise HTTPException(status_code = 404, detail = 'O livro não foi encontrado.')
    else:
        del meus_livros[id_livro]
        return {'message': 'Seu livro foi deletado com sucesso.'}