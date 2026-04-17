"""
统一响应类模块
提供标准化的API响应格式，确保所有接口返回的数据结构一致
"""
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel):
    """
    基础响应类
    所有响应类的基类，定义统一的响应结构
    """
    code: int = Field(default=200, description="响应状态码，200表示成功")
    message: str = Field(default="操作成功", description="响应消息")
    timestamp: Optional[int] = Field(default=None, description="时间戳（可选）")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "操作成功",
                "timestamp": 1234567890
            }
        }


class ApiResponse(BaseResponse, Generic[T]):
    """
    通用API响应类（带泛型）
    用于返回单个对象或任意类型的数据

    使用示例:
        return ApiResponse(data=user_info)
        return ApiResponse[UserInfo](data=user_info)
    """
    data: Optional[T] = Field(default=None, description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "查询成功",
                "data": {"id": 1, "name": "张三"}
            }
        }


class PageResponse(BaseResponse, Generic[T]):
    """
    分页响应类
    用于返回分页列表数据

    使用示例:
        return PageResponse(
            items=users,
            total=100,
            page=1,
            page_size=10
        )
    """
    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")
    total_pages: int = Field(default=0, description="总页数")

    def __init__(self, **data):
        super().__init__(**data)
        # 自动计算总页数
        if self.page_size > 0:
            self.total_pages = (self.total + self.page_size - 1) // self.page_size
        else:
            self.total_pages = 0

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "查询成功",
                "items": [{"id": 1, "name": "张三"}],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "total_pages": 10
            }
        }


class ListResponse(BaseResponse, Generic[T]):
    """
    列表响应类
    用于返回列表数据（不分页）

    使用示例:
        return ListResponse(items=users)
        return ListResponse[User](items=users)
    """
    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总记录数")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "查询成功",
                "items": [{"id": 1, "name": "张三"}],
                "total": 10
            }
        }


class SuccessResponse(BaseResponse):
    """
    成功响应类
    用于不需要返回数据的成功操作（如删除、更新等）

    使用示例:
        return SuccessResponse(message="删除成功")
    """

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "操作成功"
            }
        }


class ErrorResponse(BaseResponse):
    """
    错误响应类
    用于返回错误信息

    使用示例:
        return ErrorResponse(
            code=400,
            message="参数错误",
            errors={"field": "error message"}
        )
    """
    errors: Optional[dict] = Field(default=None, description="详细错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "message": "参数错误",
                "errors": {"username": "用户名不能为空"}
            }
        }


class ValidationErrorResponse(BaseResponse):
    """
    参数校验错误响应类
    用于返回表单验证错误信息

    使用示例:
        return ValidationErrorResponse(
            message="参数校验失败",
            details=[{"field": "email", "message": "邮箱格式不正确"}]
        )
    """
    details: List[dict] = Field(default_factory=list, description="错误详情列表")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 422,
                "message": "参数校验失败",
                "details": [
                    {"field": "email", "message": "邮箱格式不正确"},
                    {"field": "age", "message": "年龄必须大于18"}
                ]
            }
        }


class DetailResponse(BaseResponse, Generic[T]):
    """
    详情响应类
    用于返回单个对象的详细信息

    使用示例:
        return DetailResponse(data=user_detail)
    """
    data: Optional[T] = Field(default=None, description="详情数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "查询成功",
                "data": {
                    "id": 1,
                    "name": "张三",
                    "email": "zhangsan@example.com",
                    "phone": "13800138000"
                }
            }
        }


# ==================== 常用状态码常量 ====================

class ResponseCode:
    """响应状态码常量"""
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    VALIDATION_ERROR = 422

    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503


# ==================== 响应构建辅助函数 ====================

def success(data: Any = None, message: str = "操作成功", code: int = ResponseCode.SUCCESS) -> dict:
    """
    构建成功响应
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }


def success_list(items: List[Any], total: int = None, message: str = "查询成功") -> dict:
    """
    构建列表成功响应
    """
    result = {
        "code": ResponseCode.SUCCESS,
        "message": message,
        "items": items
    }
    if total is not None:
        result["total"] = total
    return result


def success_page(
    items: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 10,
    message: str = "查询成功"
) -> dict:
    """
    构建分页成功响应
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {
        "code": ResponseCode.SUCCESS,
        "message": message,
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


def error(message: str = "操作失败", code: int = ResponseCode.INTERNAL_SERVER_ERROR, errors: dict = None) -> dict:
    """
    构建错误响应
    """
    result = {
        "code": code,
        "message": message
    }
    if errors:
        result["errors"] = errors
    return result


def validation_error(message: str = "参数校验失败", details: List[dict] = None) -> dict:
    """
    构建参数校验错误响应
    """
    return {
        "code": ResponseCode.VALIDATION_ERROR,
        "message": message,
        "details": details or []
    }
