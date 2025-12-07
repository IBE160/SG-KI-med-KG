"""
Diagnostic script to verify document processing flow.
Run: python verify_flow.py
"""
import asyncio
import sys
from sqlalchemy import select, text
from app.database import async_session_maker
from app.models.document import Document
from app.models.suggestion import AISuggestion
from app.models.user import User


async def verify_flow():
    """Check each step of the document → suggestion flow."""

    print("=" * 60)
    print("DOCUMENT PROCESSING FLOW VERIFICATION")
    print("=" * 60)

    async with async_session_maker() as db:
        # Step 1: Check Documents
        print("\n[1] Checking Documents...")
        result = await db.execute(
            select(Document).order_by(Document.created_at.desc()).limit(5)
        )
        documents = result.scalars().all()

        if not documents:
            print("[ERROR] NO DOCUMENTS FOUND")
            print("   -> Upload a document via /admin/documents first")
            return

        print(f"[OK] Found {len(documents)} document(s)")
        for doc in documents:
            print(f"   - ID: {doc.id}")
            print(f"     Filename: {doc.filename}")
            print(f"     Status: {doc.status}")
            print(f"     Uploaded by: {doc.uploaded_by}")
            print(f"     Created: {doc.created_at}")

            # Get uploader info
            user_result = await db.execute(
                select(User).filter(User.id == doc.uploaded_by)
            )
            user = user_result.scalars().first()
            if user:
                print(f"     Uploader tenant_id: {user.tenant_id}")
            print()

        # Step 2: Check Suggestions
        print("\n[2] Checking AI Suggestions...")
        result = await db.execute(
            select(AISuggestion).order_by(AISuggestion.id.desc()).limit(10)
        )
        suggestions = result.scalars().all()

        if not suggestions:
            print("[ERROR] NO SUGGESTIONS FOUND")
            print("\n   Possible causes:")
            print("   1. Document status is not 'completed'")
            print("   2. Celery task failed silently")
            print("   3. AI service error")
            print("   4. Document text extraction failed")

            # Check latest document status
            latest_doc = documents[0]
            print(f"\n   Latest document status: {latest_doc.status}")
            if latest_doc.status == "pending":
                print("   -> Task never ran (check CELERY_ALWAYS_EAGER=True)")
            elif latest_doc.status == "processing":
                print("   -> Task started but didn't complete (check logs)")
            elif latest_doc.status == "failed":
                print("   -> Task failed (check backend logs)")
            elif latest_doc.status == "completed":
                print("   -> Task completed but no suggestions created")
                print("      Check AI service response")
            return

        print(f"[OK] Found {len(suggestions)} suggestion(s)")
        for sug in suggestions:
            print(f"   - ID: {sug.id}")
            print(f"     Type: {sug.type}")
            print(f"     Status: {sug.status}")
            print(f"     Document ID: {sug.document_id}")

            # Get document info
            doc_result = await db.execute(
                select(Document).filter(Document.id == sug.document_id)
            )
            doc = doc_result.scalars().first()
            if doc:
                print(f"     Document: {doc.filename}")

                # Get uploader tenant
                user_result = await db.execute(
                    select(User).filter(User.id == doc.uploaded_by)
                )
                user = user_result.scalars().first()
                if user:
                    print(f"     Tenant ID: {user.tenant_id}")
            print()

        # Step 3: Check Tenant Filtering
        print("\n[3] Checking Tenant Filtering...")

        # Get all unique tenant IDs
        result = await db.execute(text("SELECT DISTINCT tenant_id FROM \"user\""))
        tenant_ids = [row[0] for row in result.fetchall()]

        print(f"[OK] Found {len(tenant_ids)} tenant(s): {tenant_ids}")

        for tenant_id in tenant_ids:
            # Count suggestions for this tenant (using JOIN like the endpoint)
            query = text("""
                SELECT COUNT(*)
                FROM ai_suggestions
                JOIN documents ON ai_suggestions.document_id = documents.id
                JOIN "user" ON documents.uploaded_by = "user".id
                WHERE "user".tenant_id = :tenant_id
            """)
            result = await db.execute(query, {"tenant_id": tenant_id})
            count = result.scalar()

            print(f"   Tenant {tenant_id}: {count} suggestion(s)")

        # Step 4: Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        completed_docs = [d for d in documents if d.status == "completed"]
        pending_docs = [d for d in documents if d.status == "pending"]
        failed_docs = [d for d in documents if d.status == "failed"]

        print(f"Documents: {len(documents)} total")
        print(f"  - Completed: {len(completed_docs)}")
        print(f"  - Pending: {len(pending_docs)}")
        print(f"  - Failed: {len(failed_docs)}")
        print(f"Suggestions: {len(suggestions)} total")
        print(f"Tenants: {len(tenant_ids)}")

        if len(pending_docs) > 0:
            print("\n[WARNING] ISSUE: Documents stuck in 'pending' status")
            print("   -> Check CELERY_ALWAYS_EAGER in .env")
            print("   -> Restart backend server")

        if len(failed_docs) > 0:
            print("\n[WARNING] ISSUE: Documents failed processing")
            print("   -> Check backend logs for errors")

        if len(completed_docs) > 0 and len(suggestions) == 0:
            print("\n[WARNING] ISSUE: Documents completed but no suggestions")
            print("   -> Check AI service configuration")
            print("   -> Check OPENAI_API_KEY in .env")


if __name__ == "__main__":
    asyncio.run(verify_flow())
