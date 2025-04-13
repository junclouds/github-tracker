import uvicorn
from src.api_server import app

if __name__ == "__main__":
    uvicorn.run(
        "src.api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发模式下启用热重载
    ) 