"""
Create an admin user in the database.
Run this script to create a test admin account.
"""
import asyncio
import uuid
from getpass import getpass
from sqlalchemy import text
from app.database import engine
import bcrypt


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def create_admin_user():
    print("=" * 50)
    print("Create Admin User")
    print("=" * 50)

    # Get user input
    email = input("Enter admin email: ").strip()
    if not email:
        print("Error: Email is required")
        return

    password = getpass("Enter admin password: ").strip()
    if not password:
        print("Error: Password is required")
        return

    password_confirm = getpass("Confirm password: ").strip()
    if password != password_confirm:
        print("Error: Passwords don't match")
        return

    # Hash password
    hashed_password = hash_password(password)

    # Generate IDs
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()

    async with engine.begin() as conn:
        # Check if user already exists
        result = await conn.execute(
            text("SELECT id FROM \"user\" WHERE email = :email"),
            {"email": email}
        )
        existing_user = result.fetchone()

        if existing_user:
            print(f"\n❌ User with email '{email}' already exists!")

            # Ask if they want to update to admin
            update = input("Update this user to admin role? (y/n): ").strip().lower()
            if update == 'y':
                await conn.execute(
                    text("UPDATE \"user\" SET role = 'admin' WHERE email = :email"),
                    {"email": email}
                )
                print(f"✅ User '{email}' updated to admin role!")
            return

        # Create new user
        await conn.execute(
            text("""
                INSERT INTO "user"
                (id, email, hashed_password, is_active, is_superuser, is_verified, role, tenant_id)
                VALUES
                (:id, :email, :hashed_password, true, false, true, 'admin', :tenant_id)
            """),
            {
                "id": user_id,
                "email": email,
                "hashed_password": hashed_password,
                "tenant_id": tenant_id
            }
        )

        print("\n" + "=" * 50)
        print("✅ Admin user created successfully!")
        print("=" * 50)
        print(f"Email: {email}")
        print(f"Role: admin")
        print(f"User ID: {user_id}")
        print(f"Tenant ID: {tenant_id}")
        print("\nYou can now login with these credentials.")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(create_admin_user())
