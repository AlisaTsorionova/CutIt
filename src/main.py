from fastapi import FastAPI
from src.routers import links
from src.db import engine, Base
import asyncio
from contextlib import asynccontextmanager
from src.cleanup import delete_unused_links


from src.auth import fastapi_users, auth_backend
from fastapi_users.schemas import BaseUser, BaseUserCreate


class UserRead(BaseUser):
    pass


class UserCreate(BaseUserCreate):
    pass


async def cleanup():
    while True:
        await delete_unused_links()
        await asyncio.sleep(24 * 60 * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


app.include_router(links.router, prefix="/api")
