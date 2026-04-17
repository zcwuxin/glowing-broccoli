from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer

from app.middlewares.auth_middleware import create_access_token, USERS_DB, md5_encrypt
from app.scheme.auth_scheme import LoginResponse, LoginRequest

login = APIRouter()
security = HTTPBearer()


# ========== 登录接口 ==========
@login.post("/login", response_model=LoginResponse)
async def login_auth(req: LoginRequest):
    # 检查用户是否存在
    user = USERS_DB.get(req.username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # MD5 验证输入密码
    input_password_md5 = md5_encrypt(req.password)
    print("md5加密后的用户输入密码", input_password_md5)
    if input_password_md5 == user["password"]:
        # 密码合法，分发Token
        token = create_access_token(data={"sub": req.username, "role": user["role"]})
        return LoginResponse(
            code=200,
            message="登录成功",
            data={"token": token, "token_type": "bearer"}
        )

    raise HTTPException(status_code=401, detail="用户名或密码错误")
