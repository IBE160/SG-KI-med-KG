import asyncio
from app.database import async_session_maker
from app.models.document import Document
from sqlalchemy import select

async def check():
    async with async_session_maker() as db:
        result = await db.execute(
            select(Document).order_by(Document.created_at.desc()).limit(3)
        )
        docs = result.scalars().all()
        for d in docs:
            print(f"{d.filename}: {d.storage_path}")

asyncio.run(check())
