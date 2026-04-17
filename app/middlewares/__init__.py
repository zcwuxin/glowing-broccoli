from fastapi import FastAPI

from .auth_middleware import AuthMiddleware
from .cors_middleware import register_cors_middleware
from .logs_request import RequestLoggingMiddleware

def register_middlewares(app: FastAPI):
    """
    统一注册中间件
    """
    # 1. 注册 CORS 中间件（最先执行，最外层）
    # 注意：CORS 必须在其他中间件之前注册
    register_cors_middleware(app)
    # 2. 注册请求日志中间件
    app.add_middleware(RequestLoggingMiddleware)
    # 3. 注册认证中间件（最后执行，最内层）
    app.add_middleware(AuthMiddleware)
    return app
