"""
Check all users in the database and their roles.
"""
import asyncio
from sqlalchemy import text
from app.database import engine


async def check_users():
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT id, email, role, is_verified FROM \"user\" ORDER BY email")
        )
        users = result.fetchall()

        if not users:
            print("No users found in database.")
            return

        print("=" * 80)
        print("USERS IN DATABASE")
        print("=" * 80)
        for user in users:
            print(f"\nEmail:    {user[1]}")
            print(f"Role:     {user[2]}")
            print(f"Verified: {user[3]}")
            print(f"ID:       {user[0]}")
            print("-" * 80)

        print(f"\nTotal users: {len(users)}")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(check_users())
