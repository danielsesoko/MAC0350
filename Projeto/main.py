from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from Models import Item, Local, Categoria
from sqlmodel import Session, create_engine, select, SQLModel

arquivo_sqlite = "HTMX2.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as session:
        session.add_all([Categoria(nome="Documento"), Categoria(nome="Materiais"), Categoria(nome="Roupa"), Categoria(nome="Outros")])
        session.add_all([Local(nome="IME"), Local(nome="POLI"), Local(nome="Bandejao"), Local(nome="Outros")])
        session.commit()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str = ""):
    with Session(engine) as session:
        query = select(Item).where(
            (Item.cor.contains(busca)) |
            (Item.nome_pessoa.contains(busca)) |
            (Item.local_encontrado.contains(busca)))
        itens = session.exec(query).all()
        return templates.TemplateResponse(request, "lista.html", {"itens": itens})

@app.get("/editarItens", response_class=HTMLResponse)
def editar_itens(request: Request):
    with Session(engine) as session:
        categorias = session.exec(select(Categoria)).all()
        locais = session.exec(select(Local)).all()
        return templates.TemplateResponse(request, "options.html", {"categorias": categorias, "locais": locais})

@app.post("/itens", response_class=HTMLResponse)
def criar_item(categoria_id: int = Form(...), cor: str = Form(...), local_encontrado: str = Form(...), local_id: int = Form(...), nome_pessoa: str = Form(None)):
    with Session(engine) as session:
        session.add(Item(categoria_id=categoria_id, cor=cor, local_encontrado=local_encontrado, local_id=local_id, nome_pessoa=nome_pessoa))
        session.commit()
    return "<p> Item registrado, obrigado! </p>"

@app.delete("/itens", response_class=HTMLResponse)
def deletar_item(id: int = Form(...)):
    with Session(engine) as session:
        item = session.get(Item, id)
        if (not item):
            return "<p> O item não foi encontrado. </p>"
        session.delete(item)
        session.commit()
        return f"<p> Item {id} deletado. </p>"

@app.put("/itens", response_class=HTMLResponse)
def atualizar_item(id: int = Form(...)):
    with Session(engine) as session:
        item = session.get(Item, id)
        if (not item):
            return "<div>Erro: O tem não foi encontrado.</div>"
        item.status = "Recuperado"
        session.add(item)
        session.commit()
        return f"<div>O item {id} foi marcado como recuperado.</div>"
