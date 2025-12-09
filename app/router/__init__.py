from .auth import router as auth
from .user import router as user
from .station import router as station
from .data import router as data
from fastapi import FastAPI


def router_register(app: FastAPI) -> FastAPI:
    app.include_router(auth)
    app.include_router(user)
    app.include_router(station)
    app.include_router(data)
    return app
