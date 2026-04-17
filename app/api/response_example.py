"""
统一响应类使用示例
展示如何在 API 中使用统一响应类
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.scheme.common_response import (
    ApiResponse,
    PageResponse,
    ListResponse,
    SuccessResponse,
    ErrorResponse,
    DetailResponse,
    ResponseCode,
    success,
    success_list,
    success_page,
    error
)

# 假设的数据模型
class StudentModel:
    """学生数据模型示例"""
    def __init__(self, id: int, name: str, age: int, class_name: str):
        self.id = id
        self.name = name
        self.age = age
        self.class_name = class_name


example_router = APIRouter(prefix="/example", tags=["响应示例"])


# ==================== 示例1: 使用 ApiResponse ====================
@example_router.get("/students/{s_id}", response_model=ApiResponse, summary="查询单个学生信息")
async def get_student_example(s_id: int, db: Session = Depends(get_db)):
    """
    示例：查询单个学生信息
    返回类型：ApiResponse
    """
    try:
        # 模拟查询数据库
        if s_id == 404:
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail="学生不存在"
            )

        student = StudentModel(
            id=s_id,
            name="张三",
            age=20,
            class_name="计算机1班"
        )

        # 方式1：使用 ApiResponse 类
        return ApiResponse(data=student, message="查询成功")

    except HTTPException:
        raise
    except Exception as e:
        return error(
            message=f"查询失败: {str(e)}",
            code=ResponseCode.INTERNAL_SERVER_ERROR
        )


# ==================== 示例2: 使用 ListResponse ====================
@example_router.get("/students", response_model=ListResponse, summary="查询学生列表")
async def get_students_example(
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    示例：查询学生列表（不分页）
    返回类型：ListResponse
    """
    try:
        # 模拟查询数据库
        students = [
            StudentModel(id=1, name="张三", age=20, class_name="计算机1班"),
            StudentModel(id=2, name="李四", age=21, class_name="计算机2班"),
            StudentModel(id=3, name="王五", age=19, class_name="计算机1班"),
        ]

        # 方式1：使用 ListResponse 类
        return ListResponse(items=students, total=len(students))

        # 方式2：使用辅助函数 success_list
        # return success_list(items=students, total=len(students))

    except Exception as e:
        return error(message=f"查询失败: {str(e)}")


# ==================== 示例3: 使用 PageResponse ====================
@example_router.get("/students/page", response_model=PageResponse, summary="分页查询学生")
async def get_students_page_example(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    示例：分页查询学生
    返回类型：PageResponse
    """
    try:
        # 模拟查询数据库
        all_students = [
            StudentModel(id=i, name=f"学生{i}", age=18 + (i % 5), class_name=f"班级{(i % 3) + 1}班")
            for i in range(1, 101)
        ]

        # 计算分页
        total = len(all_students)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = all_students[start:end]

        # 方式1：使用 PageResponse 类（自动计算总页数）
        return PageResponse(
            items=page_items,
            total=total,
            page=page,
            page_size=page_size
        )

        # 方式2：使用辅助函数 success_page
        # return success_page(
        #     items=page_items,
        #     total=total,
        #     page=page,
        #     page_size=page_size
        # )

    except Exception as e:
        return error(message=f"查询失败: {str(e)}")


# ==================== 示例4: 使用 SuccessResponse ====================
@example_router.delete("/students/{s_id}", response_model=SuccessResponse, summary="删除学生")
async def delete_student_example(s_id: int, db: Session = Depends(get_db)):
    """
    示例：删除学生（不需要返回数据）
    返回类型：SuccessResponse
    """
    try:
        # 模拟删除操作
        if s_id == 404:
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail="学生不存在"
            )

        # 方式1：使用 SuccessResponse 类
        return SuccessResponse(message="删除成功")

    except HTTPException:
        raise
    except Exception as e:
        return error(message=f"删除失败: {str(e)}")


# ==================== 示例5: 使用 DetailResponse ====================
@example_router.get("/students/{s_id}/detail", response_model=DetailResponse, summary="查询学生详细信息")
async def get_student_detail_example(s_id: int, db: Session = Depends(get_db)):
    """
    示例：查询学生详细信息
    返回类型：DetailResponse
    """
    try:
        # 模拟查询数据库
        if s_id == 404:
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail="学生不存在"
            )

        student_detail = {
            "id": s_id,
            "name": "张三",
            "age": 20,
            "gender": "男",
            "phone": "13800138000",
            "email": "zhangsan@example.com",
            "class_name": "计算机1班",
            "major": "计算机科学与技术",
            "college": "清华大学",
            "address": "北京市海淀区",
            "hometown": "北京市",
            "study_date": "2020-09-01",
            "graduate_date": "2024-06-30"
        }

        # 使用 DetailResponse 类
        return DetailResponse(data=student_detail, message="查询成功")

    except HTTPException:
        raise
    except Exception as e:
        return error(message=f"查询失败: {str(e)}")


# ==================== 示例6: 使用 ErrorResponse ====================
@example_router.post("/students/{s_id}/validate", response_model=ErrorResponse, summary="参数校验示例")
async def validate_student_example(s_id: int, name: str = Query(..., description="学生姓名")):
    """
    示例：参数校验错误返回
    返回类型：ErrorResponse
    """
    try:
        # 模拟参数校验
        errors = {}

        if not name or len(name) < 2:
            errors["name"] = "姓名长度不能少于2个字符"

        if s_id <= 0:
            errors["s_id"] = "学生ID必须大于0"

        if errors:
            # 使用 ErrorResponse 类
            return ErrorResponse(
                code=ResponseCode.BAD_REQUEST,
                message="参数校验失败",
                errors=errors
            )

        return error(message="参数校验成功", code=ResponseCode.SUCCESS)

    except Exception as e:
        return error(message=f"校验失败: {str(e)}")


# ==================== 示例7: 创建学生 ====================
@example_router.post("/students", response_model=ApiResponse, summary="创建学生")
async def create_student_example(
    name: str = Query(..., description="学生姓名"),
    age: int = Query(..., ge=1, le=150, description="学生年龄"),
    db: Session = Depends(get_db)
):
    """
    示例：创建学生
    返回类型：ApiResponse（使用 CREATED 状态码）
    """
    try:
        # 模拟创建操作
        new_student = StudentModel(
            id=999,
            name=name,
            age=age,
            class_name="计算机1班"
        )

        # 使用 ApiResponse 类，指定 CREATED 状态码
        return ApiResponse(
            data=new_student,
            message="创建成功",
            code=ResponseCode.CREATED
        )

    except Exception as e:
        return error(
            message=f"创建失败: {str(e)}",
            code=ResponseCode.INTERNAL_SERVER_ERROR
        )


# ==================== 示例8: 更新学生 ====================
@example_router.put("/students/{s_id}", response_model=ApiResponse, summary="更新学生")
async def update_student_example(
    s_id: int,
    name: Optional[str] = Query(None, description="学生姓名"),
    age: Optional[int] = Query(None, ge=1, le=150, description="学生年龄"),
    db: Session = Depends(get_db)
):
    """
    示例：更新学生
    返回类型：ApiResponse
    """
    try:
        # 模拟更新操作
        if s_id == 404:
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail="学生不存在"
            )

        updated_student = StudentModel(
            id=s_id,
            name=name or "张三",
            age=age or 20,
            class_name="计算机1班"
        )

        return ApiResponse(
            data=updated_student,
            message="更新成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        return error(
            message=f"更新失败: {str(e)}",
            code=ResponseCode.INTERNAL_SERVER_ERROR
        )


# ==================== 示例9: 使用辅助函数 ====================
@example_router.get("/students/helper", response_model=ApiResponse, summary="使用辅助函数示例")
async def use_helper_functions(db: Session = Depends(get_db)):
    """
    示例：展示如何使用辅助函数
    """
    try:
        students = [
            StudentModel(id=1, name="张三", age=20, class_name="计算机1班"),
            StudentModel(id=2, name="李四", age=21, class_name="计算机2班"),
        ]

        # 使用不同的辅助函数
        return {
            "success_example": success(data=students[0]),
            "success_list_example": success_list(items=students, total=len(students)),
            "success_page_example": success_page(
                items=students,
                total=20,
                page=1,
                page_size=10
            ),
            "error_example": error(message="操作失败", code=ResponseCode.BAD_REQUEST)
        }

    except Exception as e:
        return error(message=f"操作失败: {str(e)}")
