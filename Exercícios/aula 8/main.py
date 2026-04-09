from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

db = {"likes": 0}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"pagina": "/home/curtidas"})

@app.get("/home/curtidas", response_class=HTMLResponse)
async def curtidas(request: Request):
    context = {"request": request, "pagina": "/home/curtidas", "likes": db["likes"]}
    if "HX-Request" not in request.headers:
        return templates.TemplateResponse(request, "index.html", context)
    return templates.TemplateResponse(request, "curtidas.html", context)

@app.get("/home/jupiter", response_class=HTMLResponse)
async def jupiter(request: Request):
    context = {"request": request, "pagina": "/home/jupiter"}
    if "HX-Request" not in request.headers:
        return templates.TemplateResponse(request, "index.html", context)
    return templates.TemplateResponse(request, "jupiter.html", context)

@app.get("/home/renata", response_class=HTMLResponse)
async def renata(request: Request):
    context = {"request": request, "pagina": "/home/renata"}
    if "HX-Request" not in request.headers:
        return templates.TemplateResponse(request, "index.html", context)
    return templates.TemplateResponse(request, "renata.html", context)

@app.post("/curtir", response_class=HTMLResponse)
async def curtir(reset: bool = False):
    if reset:
        db["likes"] = 0
    else:
        db["likes"] += 1
    return str(db["likes"])
