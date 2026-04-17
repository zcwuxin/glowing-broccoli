import os

from fastapi import FastAPI
from fastapi.security import HTTPBearer
from starlette.responses import FileResponse, Response

from app.api import class_api
from app.api.login_api import login
from app.api.statistical_analysis import statistical_analysis_router
from app.api.response_example import example_router
from app.middlewares.auth_middleware import AuthMiddleware
from core import Base,engine,settings,setup_logging,log_config
from middlewares import register_middlewares
from api import students_router,stu_offers_route,grade_router,router as teachers_router

setup_logging()
security = HTTPBearer()
app = FastAPI(
    title='人员信息管理系统',
    version='2.0 Plus',
    debug= settings.DEBUG,
    swagger_ui_parameters={
          "persistAuthorization": True  # 刷新页面后保持认证状态)
    }
)

# 手动配置 OpenAPI 安全方案
app.openapi_security_schemes = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "输入 Token，格式：Bearer &lt;your_token&gt;"
    }
}
app.openapi_security = [{"BearerAuth": []}]

register_middlewares(app)    #导入中间件
Base.metadata.create_all(engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)

@app.get("/")
async def root():
    html_path = "D:/Project/html.html"
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"message": "欢迎使用人员信息管理系统", "error": "HTML文件不存在"}

@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    """返回网站图标 - 避免 404 错误"""
    # 方法1：返回 204 No Content
    return Response(status_code=204)


# 在下面添加自己的路由
"""
app.include_router(子路由模块名.子路由实例, tags=["模块标签"])   
main里不再写专属路径！！！

# 例
app.include_router(student.router, tags=["学生模块"])
"""
app.include_router(login, tags=["登录管理"])
app.include_router(students_router, tags=["学生基本信息管理模块"])
app.include_router(stu_offers_route, tags=["学生就业管理"])
app.include_router(grade_router, tags=["成绩模块"])
app.include_router(teachers_router, tags=["老师信息管理"])
app.include_router(class_api.class_router, tags=["班级管理模块"])
app.include_router(statistical_analysis_router, tags=["统计模块"])
app.include_router(example_router, tags=["统一响应类示例"])