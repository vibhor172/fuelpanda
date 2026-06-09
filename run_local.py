
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./local_dev.db")
os.environ.setdefault("APP_ENV", "local")

import fakeredis 

import app.models  
from app.core.base_model import Base  
from app.dependencies.database import get_engine  
from app.dependencies.redis_client import get_redis  
from app.main import app  

_fake_redis = fakeredis.FakeStrictRedis(decode_responses=True)
app.dependency_overrides[get_redis] = lambda: _fake_redis

Base.metadata.create_all(get_engine())


if __name__ == "__main__":
    import uvicorn

    print("FuelPanda local dev server → http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
