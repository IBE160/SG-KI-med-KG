
import asyncio
from sqlalchemy import text
from app.database import engine

async def debug_db():
    async with engine.begin() as conn:
        print("\n=== DOCUMENTS ===")
        result = await conn.execute(text("SELECT id, filename, uploaded_by, hex(uploaded_by) as hex_id FROM documents"))
        docs = result.fetchall()
        if not docs:
            print("No documents found.")
        for d in docs:
            print(f"Doc ID: {d[0]}, File: {d[1]}, UploadedBy: {d[2]} (Type: {type(d[2])})")
            
        print("\n=== USERS ===")
        result = await conn.execute(text("SELECT id, email, hex(id) as hex_id FROM \"user\""))
        users = result.fetchall()
        for u in users:
            print(f"User ID: {u[0]}, Email: {u[1]} (Type: {type(u[0])})")

if __name__ == "__main__":
    asyncio.run(debug_db())
