from fastapi import HTTPException, Header, Depends
from sqlmodel import select
from app.database.schema import User
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.engine import get_session
from app.settings import load_settings
from typing import Annotated

async def get_current_user(
    Authorization: Annotated[str|None, Header()] = None,
    session: AsyncSession = Depends(get_session),
) -> User:
    if Authorization is None:
        raise HTTPException(status_code=401, detail="请提供有效的请求头")

    settings = load_settings()
    
    token = Authorization[7:]
    decoded_token = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    username = decoded_token["sub"]
    try:
        user = await session.execute(select(User).where(User.username == username))
        user = user.scalars().first()
        if user is None:
            raise HTTPException(status_code=401, detail="未找到用户")
        return user
    except jwt.exceptions.PyJWTError:
        raise HTTPException(status_code=401, detail="无效的jwt token")
