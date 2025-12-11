import os
from celery import Celery
from dotenv import load_dotenv
from pathlib import Path

# Load .env file explicitly from backend root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Celery configuration
CELERY_ALWAYS_EAGER = os.environ.get("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true"

# Fallback to sqlite broker if eager mode is enabled (robust local fallback)
default_broker = "sqla+sqlite:///celery.db" if CELERY_ALWAYS_EAGER else "redis://localhost:6379/0"
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", default_broker)
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "db+sqlite:///celery_results.db")

print(f"DEBUG: Celery Eager Mode: {CELERY_ALWAYS_EAGER}")
print(f"DEBUG: Celery Broker: {CELERY_BROKER_URL}")

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks.analysis"] # Explicitly include task modules
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_always_eager=CELERY_ALWAYS_EAGER,
)
