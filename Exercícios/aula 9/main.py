from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, create_engine, Session, select, func, col
from Models import Aluno

arquivo_sqlite = "HTMX2.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"
engine = create_engine(url_sqlite)

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def initFunction(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=initFunction)

def buscar_alunos_paginado(busca: str, page: int, limit: int):
    offset = (page - 1) * limit
    with Session(engine) as session:
        query = select(Aluno).where(col(Aluno.nome).contains(busca)).order_by(Aluno.nome).offset(offset).limit(limit)
        alunos = session.exec(query).all()
        
        count_query = select(func.count(Aluno.id)).where(col(Aluno.nome).contains(busca))
        total = session.exec(count_query).one()
        
        return alunos, total

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"pagina": "/lista"})

@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str = '', page: int = 1):
    limit = 2
    alunos, total_alunos = buscar_alunos_paginado(busca, page, limit)
    tem_proxima = (page * limit) < total_alunos
    
    context = {
        "request": request,
        "alunos": alunos,
        "busca": busca,
        "page": page,
        "tem_proxima": tem_proxima,
        "pagina": f"/lista?busca={busca}&page={page}"
    }

    if "HX-Request" not in request.headers:
        return templates.TemplateResponse(request, "index.html", context)
    return templates.TemplateResponse(request, "lista.html", context)

@app.get("/editarAlunos", response_class=HTMLResponse)
def editar_alunos(request: Request):
    context = {
        "request": request, 
        "pagina": "/editarAlunos"
    }
    
    if "HX-Request" not in request.headers:
        return templates.TemplateResponse(request, "index.html", context)
    return templates.TemplateResponse(request, "options.html", context)

@app.post("/novoAluno", response_class=HTMLResponse)
def criar_aluno(nome: str = Form(...)):
    with Session(engine) as session:
        novo_aluno = Aluno(nome=nome)
        session.add(novo_aluno)
        session.commit()
        return f"<p>O(a) aluno(a) <strong>{novo_aluno.nome}</strong> foi registrado(a)!</p>"

@app.put("/atualizaAluno", response_class=HTMLResponse)
def atualizar_aluno(id: int = Form(...), novoNome: str = Form(...)):
    with Session(engine) as session:
        aluno = session.get(Aluno, id)
        if not aluno:
            return "<p>Erro: Aluno não encontrado.</p>"

        nomeAntigo = aluno.nome
        aluno.nome = novoNome
        session.commit()
        return f"<p>O(a) aluno(a) {nomeAntigo} foi atualizado(a) para <strong>{aluno.nome}</strong>!</p>"

@app.delete("/deletaAluno", response_class=HTMLResponse)
def deletar_aluno(id: int = Form(...)):
    with Session(engine) as session:
        aluno = session.get(Aluno, id)
        if not aluno:
            return "<p>Erro: Aluno não encontrado.</p>"
        
        session.delete(aluno)
        session.commit()
        return f"<p>O(a) aluno(a) <strong>{aluno.nome}</strong> (ID: {id}) foi deletado(a)!</p>"
