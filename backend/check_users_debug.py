
import asyncio
from sqlalchemy import text
from app.database import engine

async def list_users():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT email, role, id FROM \"user\""))
        users = result.fetchall()
        print("\n=== USERS IN DATABASE ===")
        for u in users:
            print(f"Email: {u[0]}, Role: {u[1]}, ID: {u[2]}")
        print("=========================\n")

if __name__ == "__main__":
    asyncio.run(list_users())

