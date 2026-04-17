from pydantic import BaseModel


# 登录用请求体
class LoginRequest(BaseModel):
    username: str
    password: str


# 登陆用响应体
class LoginResponse(BaseModel):
    code: int
    message: str
    data: dict
