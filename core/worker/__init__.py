from celery import Celery
from core.config import settings

class CeleryService:

    def __init__(self, backend_url: str, broker_url:str):
        self._celery = Celery(
            "worker",
            backend=backend_url,
            broker=broker_url
        )

    @property
    def celery(self):
        return self._celery


async def get_celery_service():
    return CeleryService(
        settings.CELERY_BACKEND_URL,
        settings.CELERY_BROKER_URL
    )