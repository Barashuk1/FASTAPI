import sys
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from photoshare.routes import images, tags, auth, comment, users
import uvicorn
from photoshare.conf.config import settings

from photoshare.database.db import Session, get_db
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from photoshare.database.models import Image, Tag

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
        "/static", StaticFiles(directory="photoshare/static"), name="static"
    )

templates = Jinja2Templates(directory="photoshare/services/templates")


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
