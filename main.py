import uvicorn
from dotenv import load_dotenv

from app.core.config import settings

load_dotenv()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)
