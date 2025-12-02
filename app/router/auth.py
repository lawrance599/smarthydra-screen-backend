from fastapi import Depends, APIRouter, Form, HTTPException, status
from typing import Annotated
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database.engine import get_session
from app.database.schema import User
from sqlalchemy.exc import NoResultFound
from app.deps.jwt import make_jwt

router = APIRouter(prefix="/auth", tags=["认证"])


class Login(BaseModel):
    username: str
    password: str
    expire_minutes: int = 1440


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ErrorResponse(BaseModel):
    message: str


@router.post("")
async def login(login: Annotated[Login, Form()], session: AsyncSession = Depends(get_session)):
    """
    登录接口
    """
    statement = select(User.password).where(User.username == login.username)
    try:
        password = (await session.execute(statement)).scalar_one()
    except NoResultFound:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if password != login.password:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误")
    return TokenResponse(access_token=make_jwt(login.username, login.expire_minutes))
