import sys
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from photoshare_src.routes import images, tags, auth, comment, users
import uvicorn
from photoshare_src.conf.config import settings

from photoshare_src.database.db import Session, get_db
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from photoshare_src.database.models import Image, Tag

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
app.include_router(auth.router, prefix='/api')
app.include_router(tags.router, prefix='/photoshare')
app.include_router(users.router, prefix='/photoshare')

# If we generate the documentation with Sphinx, we need to mock the
# StaticFiles class. And if we run the application, everything will work ok.
if "sphinx" in sys.modules:
    class StaticFiles:
        def __init__(self, *args, **kwargs):
            pass
else:
    from fastapi.staticfiles import StaticFiles

if 'StaticFiles' in globals():
    app.mount(
        "/static", StaticFiles(directory="photoshare_src/static"), name="static"
    )

templates = Jinja2Templates(directory="photoshare_src/services/templates")

# @app.on_event("startup")
# async def startup():
#     r = await redis.Redis(
#         host=settings.redis_host,
#         port=settings.redis_port,
#         password=settings.redis_password,
#         db=0, encoding="utf-8", decode_responses=True
#     )
#     await FastAPILimiter.init(r)

# @app.get("/")
# def read_root():
#     """
#     The read_root function returns a dictionary with the key 'message' and
#     value &quot;Wellcome to PhotoShare API!&quot;.

#     :return: A dictionary
#     """
#     return {"message": "Wellcome to PhotoShare API!"}


@app.get("/", response_class=HTMLResponse)
async def main_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Main page for the PhotoShare application.

    :param request: The request object.
    :param db: Database session
    :return: The main page
    """
    images = db.query(Image).all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "images": images}
    )


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='localhost',
        port=8000,
        reload=True
    )
