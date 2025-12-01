from .auth import router as auth
from .user import router as user
from fastapi import FastAPI
def router_register(app: FastAPI) -> FastAPI:
    app.include_router(auth)
    app.include_router(user)
    return app