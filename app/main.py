from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.settings import load_settings
from app.database.engine import init_db
from app.router import router_register


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    load_settings()
    await init_db()

    yield


app = FastAPI(lifespan=lifespan)
app = router_register(app)
