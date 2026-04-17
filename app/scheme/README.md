# 统一响应类使用指南

本项目使用标准化的API响应格式，确保所有接口返回的数据结构一致。

## 响应类说明

### 1. ApiResponse - 通用API响应类
用于返回单个对象或任意类型的数据。

```python
from app.scheme.common_response import ApiResponse

# 方式1：不指定泛型类型
return ApiResponse(data=user_info)

# 方式2：指定泛型类型（推荐，类型提示更明确）
return ApiResponse[UserInfo](data=user_info)

# 返回示例
{
    "code": 200,
    "message": "查询成功",
    "data": {
        "id": 1,
        "name": "张三"
    }
}
```

### 2. PageResponse - 分页响应类
用于返回分页列表数据。

```python
from app.scheme.common_response import PageResponse

return PageResponse(
    items=users,
    total=100,
    page=1,
    page_size=10
)

# 返回示例
{
    "code": 200,
    "message": "查询成功",
    "items": [{"id": 1, "name": "张三"}],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
}
```

### 3. ListResponse - 列表响应类
用于返回列表数据（不分页）。

```python
from app.scheme.common_response import ListResponse

return ListResponse(items=users, total=10)

# 返回示例
{
    "code": 200,
    "message": "查询成功",
    "items": [{"id": 1, "name": "张三"}],
    "total": 10
}
```

### 4. SuccessResponse - 成功响应类
用于不需要返回数据的成功操作（如删除、更新等）。

```python
from app.scheme.common_response import SuccessResponse

return SuccessResponse(message="删除成功")

# 返回示例
{
    "code": 200,
    "message": "删除成功"
}
```

### 5. ErrorResponse - 错误响应类
用于返回错误信息。

```python
from app.scheme.common_response import ErrorResponse

return ErrorResponse(
    code=400,
    message="参数错误",
    errors={"username": "用户名不能为空"}
)

# 返回示例
{
    "code": 400,
    "message": "参数错误",
    "errors": {"username": "用户名不能为空"}
}
```

### 6. ValidationErrorResponse - 参数校验错误响应类
用于返回表单验证错误信息。

```python
from app.scheme.common_response import ValidationErrorResponse

return ValidationErrorResponse(
    message="参数校验失败",
    details=[
        {"field": "email", "message": "邮箱格式不正确"},
        {"field": "age", "message": "年龄必须大于18"}
    ]
)

# 返回示例
{
    "code": 422,
    "message": "参数校验失败",
    "details": [
        {"field": "email", "message": "邮箱格式不正确"},
        {"field": "age", "message": "年龄必须大于18"}
    ]
}
```

### 7. DetailResponse - 详情响应类
用于返回单个对象的详细信息。

```python
from app.scheme.common_response import DetailResponse

return DetailResponse(data=user_detail)

# 返回示例
{
    "code": 200,
    "message": "查询成功",
    "data": {
        "id": 1,
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000"
    }
}
```

## 辅助函数

### 1. success - 构建成功响应
```python
from app.scheme.common_response import success, ResponseCode

# 基础用法
return success(data=user_info)
return success(data=user_info, message="创建成功")

# 指定状态码
return success(data=user_info, code=ResponseCode.CREATED)

# 不返回数据
return success()
```

### 2. success_list - 构建列表成功响应
```python
from app.scheme.common_response import success_list

return success_list(items=users, total=10)
```

### 3. success_page - 构建分页成功响应
```python
from app.scheme.common_response import success_page

return success_page(
    items=users,
    total=100,
    page=1,
    page_size=10
)
```

### 4. error - 构建错误响应
```python
from app.scheme.common_response import error, ResponseCode

# 基础用法
return error(message="操作失败")

# 指定状态码
return error(message="用户不存在", code=ResponseCode.NOT_FOUND)

# 带详细错误信息
return error(
    message="参数错误",
    code=ResponseCode.BAD_REQUEST,
    errors={"username": "用户名不能为空"}
)
```

### 5. validation_error - 构建参数校验错误响应
```python
from app.scheme.common_response import validation_error

return validation_error(
    message="参数校验失败",
    details=[
        {"field": "email", "message": "邮箱格式不正确"}
    ]
)
```

## 状态码常量

使用 `ResponseCode` 类中的常量来避免硬编码状态码：

```python
from app.scheme.common_response import ResponseCode

# 常用状态码
ResponseCode.SUCCESS               # 200 - 成功
ResponseCode.CREATED              # 201 - 已创建
ResponseCode.NO_CONTENT           # 204 - 无内容
ResponseCode.BAD_REQUEST          # 400 - 请求错误
ResponseCode.UNAUTHORIZED         # 401 - 未授权
ResponseCode.FORBIDDEN            # 403 - 禁止访问
ResponseCode.NOT_FOUND            # 404 - 未找到
ResponseCode.VALIDATION_ERROR     # 422 - 参数校验错误
ResponseCode.INTERNAL_SERVER_ERROR # 500 - 服务器内部错误
```

## 完整使用示例

### 示例1：查询学生列表
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.scheme.common_response import ListResponse, ResponseCode
from app.dao.students_dao import get_students

router = APIRouter()

@router.get("/students", response_model=ListResponse)
async def get_student_list(
    db: Session = Depends(get_db)
):
    try:
        students = get_students(db, {})
        return ListResponse(items=students, total=len(students))
    except Exception as e:
        return error(
            message=f"查询失败: {str(e)}",
            code=ResponseCode.INTERNAL_SERVER_ERROR
        )
```

### 示例2：创建学生
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.scheme.common_response import ApiResponse, ResponseCode
from app.scheme.students_request import StudentsRequest
from app.dao.students_dao import create_student

@router.post("/students", response_model=ApiResponse)
async def create_student_api(
    student: StudentsRequest,
    db: Session = Depends(get_db)
):
    try:
        new_student = create_student(db, student)
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
```

### 示例3：分页查询
```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.scheme.common_response import PageResponse
from app.dao.students_dao import get_students_paginated

@router.get("/students/page", response_model=PageResponse)
async def get_student_list_page(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    try:
        result = get_students_paginated(db, page, page_size)
        return PageResponse(
            items=result["items"],
            total=result["total"],
            page=page,
            page_size=page_size
        )
    except Exception as e:
        return error(message=f"查询失败: {str(e)}")
```

### 示例4：更新学生
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.scheme.common_response import SuccessResponse, ResponseCode
from app.scheme.students_request import StudentsRequest
from app.dao.students_dao import update_student

@router.patch("/students/{s_id}", response_model=SuccessResponse)
async def update_student_api(
    s_id: int,
    student: StudentsRequest,
    db: Session = Depends(get_db)
):
    try:
        updated = update_student(db, s_id, student)
        if not updated:
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail="学生不存在"
            )
        return SuccessResponse(message="更新成功")
    except HTTPException:
        raise
    except Exception as e:
        return error(message=f"更新失败: {str(e)}")
```

### 示例5：删除学生
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.scheme.common_response import SuccessResponse, ResponseCode
from app.dao.students_dao import delete_student

@router.delete("/students/{s_id}", response_model=SuccessResponse)
async def delete_student_api(
    s_id: int,
    db: Session = Depends(get_db)
):
    try:
        success = delete_student(db, s_id)
        if not success:
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail="学生不存在"
            )
        return SuccessResponse(message="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        return error(message=f"删除失败: {str(e)}")
```

## 最佳实践

1. **使用泛型类型**：在可能的情况下，为 `ApiResponse` 和 `ListResponse` 指定泛型类型，以获得更好的类型提示。

2. **统一错误处理**：在全局异常处理器中使用统一响应类。

3. **使用状态码常量**：避免硬编码状态码，使用 `ResponseCode` 常量。

4. **返回明确的消息**：为每个操作提供清晰、友好的消息提示。

5. **一致性**：在整个项目中保持相同的响应格式，不要混用不同的响应结构。

## 迁移指南

如果项目中有旧的响应格式，可以按以下步骤迁移：

1. 在 `app/scheme/__init__.py` 中已导出新的统一响应类
2. 逐步替换旧的响应类为新的统一响应类
3. 更新 API 文档中的 `response_model` 定义
4. 更新前端代码以适配新的响应格式

示例：
```python
# 旧的
return {"code": 200, "message": "成功", "data": student}

# 新的
return ApiResponse(data=student)
```
