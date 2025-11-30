from fastapi import Depends, APIRouter, Form, HTTPException, status
from typing import Annotated
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database.engine import get_session
from app.database.schema import User
from sqlalchemy.exc import NoResultFound
from app.jwt import make_jwt
from app.database.schema import UserRole
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

class Login(BaseModel):
    username: str
    password: str
    expire_minutes: int =1440

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ErrorResponse(BaseModel):
    message: str
@router.post("")
async def login(login: Annotated[Login, Form()], session: AsyncSession=Depends(get_session)):
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
class Register(BaseModel):
    username: str
    password: str
    role: str = "user"

@router.post("/register")
async def register(register: Annotated[Register, Form()], session: AsyncSession=Depends(get_session)):
    """
    注册接口
    """
    statement = select(User).where(User.username == register.username)
    try:
        user = (await session.execute(statement)).scalar_one()
    except NoResultFound:
        user = None
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户已存在")
    else:
        new_user = User(
            username=register.username,
            password=register.password,
            role=UserRole(register.role),
            is_active=True
        )
        session.add(new_user)
        await session.commit()
        return TokenResponse(access_token=make_jwt(register.username))
    
@router.get("")
async def get_current_user(session: AsyncSession=Depends(get_session)):
    """
    获取当前用户信息
    """
    return {"username": "admin"}