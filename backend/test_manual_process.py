"""
Test script to manually trigger document processing via API.
This bypasses Celery and calls the processing function directly.
"""
import asyncio
import sys
from uuid import UUID
from tasks.analysis import _process_document_async

async def test_process(document_id_str: str):
    """Test processing a specific document."""
    document_id = UUID(document_id_str)

    print("=" * 60)
    print(f"MANUAL DOCUMENT PROCESSING TEST")
    print(f"Document ID: {document_id}")
    print("=" * 60)
    print()

    try:
        await _process_document_async(document_id)
        print("\n" + "=" * 60)
        print("SUCCESS: Processing completed")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_manual_process.py <document_id>")
        print("\nAvailable document IDs from verification:")
        print("  8d2fb39e-b013-47eb-bb8e-3c53755336ce (AML - Arbeidsmiljøloven EN.pdf)")
        print("  4de31b6a-b99d-4a48-963c-694493a10afd (AML - Arbeidsmiljøloven EN 2.pdf)")
        sys.exit(1)

    asyncio.run(test_process(sys.argv[1]))
