"""
Create a test BPO user with predefined credentials.
Email: bpo@test.com
Password: Bpo123!
"""
import asyncio
import uuid
from sqlalchemy import text
from app.database import engine
import bcrypt


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def create_test_bpo():
    # Predefined credentials
    email = "bpo@test.com"
    password = "Bpo123!"

    # Hash password
    hashed_password = hash_password(password)

    # Generate IDs
    user_id = uuid.uuid4()
    # Use same tenant as admin if possible, or new one. 
    # For simplicity, generating new one, but in real app admin invites BPO to tenant.
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
            
            # Update to bpo if not already
            if existing_user[1] != 'bpo':
                await conn.execute(
                    text("UPDATE \"user\" SET role = 'bpo' WHERE email = :email"),
                    {"email": email}
                )
                print(f"SUCCESS: Updated user to bpo role!")
            else:
                print(f"SUCCESS: User already has bpo role!")
                
            print(f"\nEmail: {email}")
            print(f"Password: {password}")
            return

        # Create new user
        await conn.execute(
            text("""
                INSERT INTO \"user\"
                (id, email, hashed_password, is_active, is_superuser, is_verified, role, tenant_id)
                VALUES
                (:id, :email, :hashed_password, true, false, true, 'bpo', :tenant_id)
            """),
            {
                "id": str(user_id),
                "email": email,
                "hashed_password": hashed_password,
                "tenant_id": str(tenant_id)
            }
        )

        print("\n" + "=" * 60)
        print("SUCCESS: TEST BPO USER CREATED!")
        print("=" * 60)
        print(f"Email:     {email}")
        print(f"Password:  {password}")
        print(f"User ID:   {str(user_id)}")
        print(f"Tenant ID: {str(tenant_id)}")
        print(f"Role:      bpo")
        print("=" * 60)
        print("\nYou can now login at: http://localhost:3000")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(create_test_bpo())
