import uvicorn
from core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        str("core.asgi:app"), reload=True if settings.DEBUG else False, workers=1
    )
