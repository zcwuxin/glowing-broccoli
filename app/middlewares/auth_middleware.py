import hashlib
import os

from dotenv import load_dotenv
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
from jose import jwt, JWTError  # pip install python-jose[cryptography] passlib[bcrypt]
from fastapi import Request, HTTPException, Depends

load_dotenv()



# 白名单常量
WHITELIST = ['/openapi.json', '/login', "/docs", "/",'/redoc','/api-info','/favicon.ico']

# ========== JWT 配置（从环境变量读取） ==========
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ========== MD5 加密工具函数 ==========
def md5_encrypt(text: str) -> str:
    # 使用 MD5 加密字符串
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def verify_md5(plain_text: str, encrypted_text: str) -> bool:
    # 验证明文和 MD5 密文是否匹配
    return md5_encrypt(plain_text) == encrypted_text


# ========== 从环境变量加载用户数据库 ==========
def load_users_from_env() -> dict:
    """从环境变量加载用户数据库"""
    users_db = {}
    admin_username = os.getenv("ADMIN_USERNAME", "abcde")
    admin_password_md5 = os.getenv("ADMIN_PASSWORD_MD5", "abcde")
    admin_role = os.getenv("ADMIN_ROLE", "abc")

    users_db[admin_username] = {
        "password": admin_password_md5,
        "role": admin_role
    }
    return users_db

# 加载用户数据库
USERS_DB = load_users_from_env()

# ========== JWT 工具函数 ==========
# 生成新的Token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 解码Token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="无效或过期的token")

# ========== 中间件类 ==========
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # OPTIONS预检请求直接放行
        if request.method == "OPTIONS":
            # 直接放行 OPTIONS 请求，不进行任何认证
            response = await call_next(request)
            return response
        # 白名单放行
        if request.url.path in WHITELIST:
            return await call_next(request)

        # 获取 Authorization 头
        auth_header = request.headers.get("Authorization")
        # 判断请求头中身份模块是否合法
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "缺少或无效的认证头"}
            )
        # 解码Token
        token = auth_header.split(" ")[1]
        try:
            payload = decode_token(token)
            # 存入请求状态
            request.state.user = payload
        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": str(e)}
            )

        response = await call_next(request)
        return response
