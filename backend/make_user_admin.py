"""
Make a user an admin by email.
"""
import asyncio
import sys
from sqlalchemy import text
from app.database import engine


async def make_admin(email: str):
    async with engine.begin() as conn:
        # Check if user exists
        result = await conn.execute(
            text("SELECT id, role FROM \"user\" WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()

        if not user:
            print(f"ERROR: User '{email}' not found!")
            return

        if user[1] == "admin":
            print(f"User '{email}' is already an admin!")
            return

        # Update to admin and ensure active
        await conn.execute(
            text("UPDATE \"user\" SET role = 'admin', is_verified = true, is_active = true WHERE email = :email"),
            {"email": email}
        )

        print("=" * 60)
        print(f"SUCCESS: User '{email}' is now an admin!")
        print("=" * 60)
        print("\nPlease LOGOUT and LOGIN again for changes to take effect.")
        print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_user_admin.py <email>")
        print("Example: python make_user_admin.py user@example.com")
        sys.exit(1)

    email = sys.argv[1]
    asyncio.run(make_admin(email))
