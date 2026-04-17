"""
数据模型导出模块
统一导出所有的请求和响应模型
"""

# 导出统一响应类
from .common_response import (
    ApiResponse,
    PageResponse,
    ListResponse,
    SuccessResponse,
    ErrorResponse,
    ValidationErrorResponse,
    DetailResponse,
    ResponseCode,
    success,
    success_list,
    success_page,
    error,
    validation_error
)

# 导出业务相关模型
from .stu_offers_response import stu_info_front, stu_info_del
from .stu_offers_request import stu_info_del, stu_info_front, stu_info_alter

__all__ = [
    # 统一响应类
    "ApiResponse",
    "PageResponse",
    "ListResponse",
    "SuccessResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    "DetailResponse",
    "ResponseCode",
    "success",
    "success_list",
    "success_page",
    "error",
    "validation_error",
    # 业务相关模型
    "stu_info_front",
    "stu_info_del",
    "stu_info_alter",
]