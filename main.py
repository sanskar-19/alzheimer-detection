import uvicorn
from config import setting

if __name__ == "__main__":
    # defining the entry point for our server
    uvicorn.run(
        "server.app:app",
        host=setting.HOST,
        port=setting.PORT,
        reload=True,
    )
