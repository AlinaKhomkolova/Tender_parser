import uvicorn
from apps.api.routes import app

if __name__ == "__main__":
    uvicorn.run("apps.api.routes:app", host="127.0.0.1", port=8000, reload=True)
