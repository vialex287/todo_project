import asyncio

import uvicorn
from fastapi import FastAPI

from app.api.routers import router_auth, router_tasks, router_users
from app.core.database import Base, engine

app = FastAPI()


# create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы успешно созданы в базе данных!")


@app.on_event("startup")
async def startup_event():
    await create_tables()


# view headers
app.include_router(router_users)
app.include_router(router_tasks)
app.include_router(router_auth)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
