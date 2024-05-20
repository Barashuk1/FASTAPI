
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from photoshare.routes import images, auth,comment
import uvicorn
# from photoshare.conf.config import settings

from photoshare.database.db import Session, get_db
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from photoshare.database.models import Image

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images.router, prefix='/photoshare')
app.include_router(comment.router, prefix='/photoshare')
app.mount("/static", StaticFiles(directory="photoshare/static"), name="static")
app.include_router(auth.router, prefix='/api')

templates = Jinja2Templates(directory="photoshare/templates")

# @app.on_event("startup")
# async def startup():
#     r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
#                           decode_responses=True)
#     await FastAPILimiter.init(r)

# @app.get("/")
# def read_root():
#     """
#     The read_root function returns a dictionary with the key 'message' and
#     value &quot;Contact manager API&quot;.

#     :return: A dictionary
#     """
#     return {"message": "Wellcome to PhotoShare API!"}


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request, db: Session = Depends(get_db)):
    images = db.query(Image).all()
    return templates.TemplateResponse("index.html", {"request": request, "images": images})

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )
