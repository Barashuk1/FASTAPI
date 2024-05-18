
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from photoshare.routes import images
import uvicorn
# from photoshare.conf.config import settings

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

# @app.on_event("startup")
# async def startup():
#     r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
#                           decode_responses=True)
#     await FastAPILimiter.init(r)

@app.get("/")
def read_root():
    """
    The read_root function returns a dictionary with the key 'message' and
    value &quot;Contact manager API&quot;.

    :return: A dictionary
    """
    return {"message": "Wellcome to PhotoShare API!"}

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )