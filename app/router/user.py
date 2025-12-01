from typing import Annotated
from fastapi import APIRouter, Form, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from app.deps.user import get_current_user
from app.database.engine import get_session
from app.deps.jwt import make_jwt
from sqlmodel import select
from pydantic import BaseModel
from app.database.schema import User, UserRole
from .auth import TokenResponse

router = APIRouter(prefix="/user", tags=["用户"])




class Register(BaseModel):
    username: str
    password: str
    role: str = "user"


@router.post("/register")
async def register(
    register: Annotated[Register, Form()], session: AsyncSession = Depends(get_session)
):
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
            is_active=True,
        )
        session.add(new_user)
        await session.commit()
        return TokenResponse(access_token=make_jwt(register.username))


@router.get("/me")
async def me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    获取当前用户信息
    """
    return current_user