from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn

app = FastAPI(version="v1")
templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan():
    yield

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": []})

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)