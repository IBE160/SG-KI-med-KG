
import sys
import os
from pathlib import Path

# Add backend dir to sys.path
sys.path.append(os.getcwd())

print("Testing Celery Config...")
try:
    from app.core import celery_app
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
