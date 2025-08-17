import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .db import init_db, get_session
from .models import Message
from .schemas import MessageOut
from .whatsapp import router as whatsapp_router
from .config import settings

app = FastAPI(title=settings.APP_NAME)
app.include_router(whatsapp_router)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENV}

@app.get("/messages", response_model=list[MessageOut])
async def list_messages(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Message).order_by(Message.created_at.desc()).limit(100))
    return [MessageOut.model_validate(m) for m in res.scalars().all()]

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=False)
