
import asyncio
from sqlalchemy import text
from app.database import engine

async def make_bpo():
    email = "kjamtli@hotmail.com"
    async with engine.begin() as conn:
        # Check user
        result = await conn.execute(text("SELECT id, role FROM \"user\" WHERE email = :email"), {"email": email})
        user = result.fetchone()
        
        if not user:
            print(f"User {email} not found!")
            return

        # Update
        await conn.execute(
            text("UPDATE \"user\" SET role = 'bpo' WHERE email = :email"),
            {"email": email}
        )
        print(f"SUCCESS: User {email} is now a BPO.")

if __name__ == "__main__":
    asyncio.run(make_bpo())

