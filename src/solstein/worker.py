"""
Celery worker entrypoint.
"""

from celery import Celery

from .config import get_settings

settings = get_settings()

celery_app = Celery(
    "solstein",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=["solstein.tasks"]
)

celery_app.conf.update(
    task_serializer=settings.celery.task_serializer,
    result_serializer=settings.celery.result_serializer,
    accept_content=settings.celery.accept_content,
    timezone=settings.celery.timezone,
    enable_utc=settings.celery.enable_utc,
    task_track_started=True,
)

if __name__ == "__main__":
    celery_app.start()
