import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.suggestion import AISuggestion
from app.models.user import User
from app.models.compliance import Control

# Force correct DB URL for local Supabase connection
DB_URL = "postgresql+asyncpg://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

async def check_data_integrity():
    print(f"Connecting to: {DB_URL}")
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Fetch the Control "Whistleblowing"
        print("\n--- Checking Control 'Whistleblowing' ---")
        result = await session.execute(select(Control).where(Control.name == "Whistleblowing"))
        control = result.scalar_one_or_none()
        
        if not control:
            print("Control 'Whistleblowing' NOT FOUND.")
            return

        print(f"Control ID: {control.id}")
        print(f"Current Owner ID: {control.owner_id}")

        # 2. Find the Suggestion that created it (assuming we can link them, usually via name match or if we stored suggestion_id on control - we don't seem to store suggestion_id on control directly in the model I read earlier, but audit logs might have it. Or simple name match.)
        # The prompt implies the suggestion exists.
        print("\n--- Checking Related Suggestion ---")
        # We search by content->name match since there's no direct FK
        # Note: In the previous turn, the user mentioned: "Owner should be as per assigned in .../suggestions"
        
        # We need to cast the JSON content field or fetch all and filter in python if simple filter fails
        # Trying to fetch all suggestions for inspection
        result = await session.execute(select(AISuggestion))
        suggestions = result.scalars().all()
        
        matching_suggestion = None
        for s in suggestions:
            # content is a dict
            if s.content.get("name") == "Whistleblowing":
                matching_suggestion = s
                break
        
        if matching_suggestion:
            print(f"Found Matching Suggestion ID: {matching_suggestion.id}")
            print(f"Suggestion Assigned BPO ID: {matching_suggestion.assigned_bpo_id}")
            
            if matching_suggestion.assigned_bpo_id:
                # Fetch that user details
                user_res = await session.execute(select(User).where(User.id == matching_suggestion.assigned_bpo_id))
                bpo_user = user_res.scalar_one_or_none()
                if bpo_user:
                    print(f"Assigned BPO Email: {bpo_user.email}")
            
            if str(matching_suggestion.assigned_bpo_id) != str(control.owner_id):
                print(f"⚠️ MISMATCH DETECTED: Control Owner ({control.owner_id}) != Suggestion Assignee ({matching_suggestion.assigned_bpo_id})")
            else:
                print("✅ Data Match: Control Owner matches Suggestion Assignee.")
        else:
            print("No suggestion found with content.name == 'Whistleblowing'")

        # 3. Check for ORPHANED records (Owner is None)
        print("\n--- Checking for Orphaned Records (Owner is None) ---")
        # Controls
        result = await session.execute(select(Control).where(Control.owner_id == None))
        orphans = result.scalars().all()
        print(f"Orphaned Controls: {len(orphans)}")
        
        # We generally should assume Risks and BP also need owners?
        # Let's check logic implies generic entity creation needs owner.

if __name__ == "__main__":
    asyncio.run(check_data_integrity())
