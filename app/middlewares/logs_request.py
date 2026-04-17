import uuid
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
from loguru import logger
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    中间件：为每个请求生成唯一的 Request ID，并注入 Loguru 上下文
    同时验证 Secret ID
    """

    async def dispatch(self, request: Request, call_next):
        # 1. 验证 Secret ID（除了白名单路径）
        secret_id = request.headers.get("X-Secret-ID")
        expected_secret_id = os.getenv("API_SECRET_ID", "")

        # 白名单路径（不需要验证 Secret ID）
        whitelist_paths = [
            "/docs",
            "/openapi.json",
            "/redoc",
            "/",
            "/login",
            "D:/Project/html.html"
        ]

        # 检查当前路径是否在白名单中
        is_whitelisted = any(request.url.path.startswith(path) for path in whitelist_paths)

        if not is_whitelisted and expected_secret_id:
            if not secret_id or secret_id != expected_secret_id:
                logger.warning(f"无效的 Secret ID 来自 {request.client.host}: {secret_id}")
                return JSONResponse(
                    status_code=401,
                    content={
                        "code": 401,
                        "message": "无效的 Secret ID",
                        "detail": "请提供有效的 X-Secret-ID 请求头"
                    }
                )

        # 2. 生成 Request ID (如果请求头里已经有，则复用，否则新建)
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # 3. 使用 contextualize 注入上下文
        with logger.contextualize(request_id=request_id):
            # 记录请求开始（可选）
            logger.info(f"收到请求: {request.method} {request.url.path} | 客户端: {request.client.host}")

            # 4. 处理请求
            response = await call_next(request)

            # 5. 将 Request ID 放入响应头，方便前端排查问题
            response.headers["X-Request-ID"] = request_id

            return response