from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dao import students_dao
from app.dao.students_dao import post_student, get_students
from app.scheme.students_request import StudentsRequest, StudentsQueryRequest, StudentsRequestWJC, \
    StudentsQueryRequestWJC
from app.scheme.students_response import ApiResponse, StudentInfo
from typing import List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from fastapi.responses import Response
from app.scheme.students_request import StudentsRequest, StudentsQueryRequest, get_student_query_params
from app.scheme.students_response import StudentsResponse

students_router = APIRouter()
security = HTTPBearer()
# ====================== 更新学生 ======================
@students_router.patch("/students/{s_id}", response_model=ApiResponse[StudentInfo],summary='修改学生信息')
async def update_student(s_id: int, student: StudentsRequest, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    data = students_dao.update_student(db, s_id, student)
    if not data:
        raise HTTPException(status_code=404, detail="学生不存在")
    return ApiResponse(message="更新成功", data=data)

# ====================== 删除学生 ======================
@students_router.delete("/students/{s_id}",response_model=ApiResponse,summary='删除学生信息')
async def delete_student_api(s_id: int, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    success = students_dao.delete_student(db, s_id)
    if not success:
        raise HTTPException(status_code=404, detail="学生不存在")
    return ApiResponse(message="删除成功")



# ==========================================
# 1. 添加学生 (POST)
# ==========================================
# class StudentsResponseWJC:
#     pass
#

@students_router.post(
    "/students",
    response_model=StudentsResponse,
    summary="添加学生信息"   #在线API文档显示字段
)
async def create_student(
        student_req: StudentsRequestWJC,
        db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """    这里会写入到 在线API文档中
    创建一个新的学生记录。
    注意：s_id 由数据库自动生成，无需传入。
    """
    try:
        new_student_orm = post_student(db, student_req)

        # 将 ORM 对象直接返回，Pydantic 会自动将其转换为 StudentsResponse
        # 前提是 StudentsResponse 中配置了 from_attributes = True (Pydantic V2)
        # 或者使用 orm_mode = True (Pydantic V1)

        # 转换为模型

        return new_student_orm
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建学生失败: {str(e)}")


# ==========================================
# 2. 查询学生列表 (GET)
# ==========================================
@students_router.get(
    "/students",
    #告诉 FastAPI文档：“这个接口返回的是 一组 学生数据”。
    #如果写成  response_model=StudentsResponse
    # 会告诉 FastAPI 文档：“这个接口返回的是 单个 学生对象”。
    response_model=List[StudentsResponse],
    summary="查询学生信息",   #在线API文档显示字段
)
async def get_student_list(

        #如果不写= Depends() FASTAPI会认为是从请求体中读取参数，但是GET请求没有请求体
        #有了= Depends()，fastapi知道是从URL中读取参数，会自动创建一个StudentsQueryRequest对象
        #然后把查询参数的值对应填进去，然后把这个对象赋值给query_params
     query_params: StudentsQueryRequestWJC = Depends(get_student_query_params),  # Depends() ：告诉 FastAPI 从 URL 查询参数中自动解析
     db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    根据条件筛选学生列表。
    支持：姓名/籍贯模糊搜索、年龄/入学时间范围筛选、班级/专业精确匹配等。
    示例 URL:
    /students?s_name=张&s_home=北京&s_age_min=18&s_age_max=22
    """
    print(query_params.dict())
    try:
        # 将 Pydantic 模型转换为字典，排除 None 值，传给 DAO 层
        # exclude_none=True 确保只传递用户实际填写的参数
        print('try:-------------------------------')
        params_dict = query_params.dict(exclude_none=True)
        print(params_dict)

        students_list_orm = get_students(db, params_dict)
        print(f'*{students_list_orm}')

        #转换为模型

        return students_list_orm

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询学生失败: {str(e)}")





