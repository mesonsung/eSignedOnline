#!/usr/bin/env python3
import asyncio
import uvicorn
import os
from multiprocessing import Process

def start_http_server():
    """啟動 HTTP 服務器"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7443,
        reload=False
    )

def start_https_server():
    """啟動 HTTPS 服務器"""
    ssl_keyfile = "/app/certs/key.pem"
    ssl_certfile = "/app/certs/cert.pem"
    
    if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=7444,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            reload=False
        )

if __name__ == "__main__":
    # 啟動 HTTP 服務器
    http_process = Process(target=start_http_server)
    http_process.start()
    
    # 啟動 HTTPS 服務器
    https_process = Process(target=start_https_server)
    https_process.start()
    
    try:
        # 等待兩個進程
        http_process.join()
        https_process.join()
    except KeyboardInterrupt:
        # 終止進程
        http_process.terminate()
        https_process.terminate()
        http_process.join()
        https_process.join()
