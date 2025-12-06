from app.core.celery_app import celery_app

# Import tasks here to ensure they are registered when Celery starts
from tasks.analysis import process_document
