from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = 'sqlite:///./livros.db'

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LivrosDB(Base):
    __tablename__ = "Livros"
    id_livro = Column(Integer, primary_key=True, index=True)
    nome_livro = Column(String, index=True)
    autor_livro = Column(String, index=True)
    ano_livro = Column(Integer)

Base.metadata.create_all(bind=engine)

class LivrosFormato(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

    class Config:
        from_attributes = True

app = FastAPI()

MEU_USUARIO = 'admin'
MINHA_SENHA = 'admin'

security = HTTPBasic()

def autenticar_meu_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, MEU_USUARIO)
    is_password_correct = secrets.compare_digest(credentials.password, MINHA_SENHA)
    
    if not (is_password_correct and is_username_correct):
        raise HTTPException(
            status_code=401,
            detail='Usuario ou senha incorretos.',
            headers={'WWW-Authenticate': 'Basic'}
        )
    return credentials.username

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/livros')
def get_livros(db: Session = Depends(get_db), username: str = Depends(autenticar_meu_usuario)):
    livros = db.query(LivrosDB).all()
    if not livros:
        return {'mensagem': 'A livraria está vazia.'}
    return {'livros': livros}

@app.post('/adicionar')
def post_livros(id_livro: int, livro: LivrosFormato, db: Session = Depends(get_db), username: str = Depends(autenticar_meu_usuario)):
    livro_existente = db.query(LivrosDB).filter(LivrosDB.id_livro == id_livro).first()
    if livro_existente:
        raise HTTPException(status_code=400, detail='Esse livro ja foi registrado.')
    
    novo_livro = LivrosDB(
        id_livro=id_livro,
        nome_livro=livro.nome_livro,
        autor_livro=livro.autor_livro,
        ano_livro=livro.ano_livro
    )
    db.add(novo_livro)
    db.commit()
    return {'message': 'Livro adicionado com sucesso'}

@app.put('/atualizar/{id_livro}')
def put_livros(id_livro: int, livro: LivrosFormato, db: Session = Depends(get_db), username: str = Depends(autenticar_meu_usuario)):
    meu_livro = db.query(LivrosDB).filter(LivrosDB.id_livro == id_livro).first()
    if not meu_livro:
        raise HTTPException(status_code=404, detail='O livro não foi encontrado.')
    
    meu_livro.nome_livro = livro.nome_livro
    meu_livro.autor_livro = livro.autor_livro
    meu_livro.ano_livro = livro.ano_livro
    db.commit()
    return {'message': 'Livro atualizado com sucesso.'}

@app.delete('/deletar/{id_livro}')
def delete_livros(id_livro: int, db: Session = Depends(get_db), username: str = Depends(autenticar_meu_usuario)):
    meu_livro = db.query(LivrosDB).filter(LivrosDB.id_livro == id_livro).first()
    if not meu_livro:
        raise HTTPException(status_code=404, detail='O livro não foi encontrado.')
    
    db.delete(meu_livro)
    db.commit()
    return {'message': 'Seu livro foi deletado com sucesso.'}