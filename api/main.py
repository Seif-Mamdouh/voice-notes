from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from db import Base, engine  # noqa: E402
from routers.transcriptions import router as transcriptions_router  # noqa: E402


def create_app() -> FastAPI:
    Base.metadata.create_all(engine)

    app = FastAPI(title="Voice Notes API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(transcriptions_router)
    return app


app = create_app()
