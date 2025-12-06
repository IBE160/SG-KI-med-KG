"""
Create a test admin user with predefined credentials.
Email: admin@test.com
Password: Admin123!
"""
import asyncio
import uuid
from sqlalchemy import text
from app.database import engine
import bcrypt


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def create_test_admin():
    # Predefined credentials
    email = "admin@test.com"
    password = "Admin123!"

    # Hash password
    hashed_password = hash_password(password)

    # Generate IDs
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()

    async with engine.begin() as conn:
        # Check if user already exists
        result = await conn.execute(
            text("SELECT id, role FROM \"user\" WHERE email = :email"),
            {"email": email}
        )
        existing_user = result.fetchone()

        if existing_user:
            print(f"\nWARNING: User '{email}' already exists!")

            # Update to admin if not already
            if existing_user[1] != 'admin':
                await conn.execute(
                    text("UPDATE \"user\" SET role = 'admin' WHERE email = :email"),
                    {"email": email}
                )
                print(f"SUCCESS: Updated user to admin role!")
            else:
                print(f"SUCCESS: User already has admin role!")

            print(f"\nEmail: {email}")
            print(f"Password: {password}")
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

        print("\n" + "=" * 60)
        print("SUCCESS: TEST ADMIN USER CREATED!")
        print("=" * 60)
        print(f"Email:     {email}")
        print(f"Password:  {password}")
        print(f"User ID:   {user_id}")
        print(f"Tenant ID: {tenant_id}")
        print(f"Role:      admin")
        print("=" * 60)
        print("\nYou can now login at: http://localhost:3000")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(create_test_admin())
