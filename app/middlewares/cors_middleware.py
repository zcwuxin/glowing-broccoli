# middlewares/cors_middleware.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def register_cors_middleware(app: FastAPI):
    """
    注册 CORS 跨域中间件

    注意：CORS 中间件应该在其他中间件之前添加（最先执行）
    """
    # 允许的源列表
    origins = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:80",
        "http://192.168.62.232",  # 添加你的 IP 地址
        "http://192.168.62.232:80",
        "*",  # 开发环境可以使用 *，生产环境请指定具体域名
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 或使用 ["*"] 允许所有
        allow_credentials=True,  # 允许携带认证信息
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],  # 允许所有 HTTP 方法
        allow_headers=[
            "Access-Control-Allow-Headers",
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With",
            "X-Secret-ID",
            "X-Request-ID",
        ],  # 允许所有请求头
        expose_headers=["Content-Length", "X-Request-ID", "X-Request-Id"],  # 暴露响应头
        max_age=3600,  # 预检请求缓存时间（秒）
    )

    return app