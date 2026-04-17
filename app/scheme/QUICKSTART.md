# 统一响应类快速入门

## 快速开始

### 1. 导入响应类

```python
from app.scheme.common_response import (
    ApiResponse,      # 通用API响应
    PageResponse,     # 分页响应
    ListResponse,     # 列表响应
    SuccessResponse,  # 成功响应
    ErrorResponse,    # 错误响应
    DetailResponse,   # 详情响应
    ResponseCode,     # 状态码常量
)
```

### 2. 常用场景

#### 查询单个对象
```python
@router.get("/students/{s_id}", response_model=ApiResponse)
async def get_student(s_id: int):
    student = get_student_from_db(s_id)
    return ApiResponse(data=student, message="查询成功")
```

#### 查询列表（不分页）
```python
@router.get("/students", response_model=ListResponse)
async def get_students():
    students = get_all_students_from_db()
    return ListResponse(items=students, total=len(students))
```

#### 分页查询
```python
@router.get("/students/page", response_model=PageResponse)
async def get_students_page(page: int = 1, page_size: int = 10):
    result = get_students_paginated(page, page_size)
    return PageResponse(
        items=result["items"],
        total=result["total"],
        page=page,
        page_size=page_size
    )
```

#### 创建数据
```python
@router.post("/students", response_model=ApiResponse)
async def create_student(student: StudentCreate):
    new_student = create_student_in_db(student)
    return ApiResponse(
        data=new_student,
        message="创建成功",
        code=ResponseCode.CREATED  # 201
    )
```

#### 更新数据
```python
@router.put("/students/{s_id}", response_model=ApiResponse)
async def update_student(s_id: int, student: StudentUpdate):
    updated_student = update_student_in_db(s_id, student)
    return ApiResponse(data=updated_student, message="更新成功")
```

#### 删除数据
```python
@router.delete("/students/{s_id}", response_model=SuccessResponse)
async def delete_student(s_id: int):
    delete_student_in_db(s_id)
    return SuccessResponse(message="删除成功")
```

#### 查询详情
```python
@router.get("/students/{s_id}/detail", response_model=DetailResponse)
async def get_student_detail(s_id: int):
    detail = get_student_detail_from_db(s_id)
    return DetailResponse(data=detail, message="查询成功")
```

### 3. 错误处理

#### HTTP 异常
```python
from fastapi import HTTPException

@router.get("/students/{s_id}")
async def get_student(s_id: int):
    student = get_student_from_db(s_id)
    if not student:
        raise HTTPException(
            status_code=ResponseCode.NOT_FOUND,
            detail="学生不存在"
        )
    return ApiResponse(data=student)
```

#### 业务错误返回
```python
@router.post("/students")
async def create_student(student: StudentCreate):
    if not validate_student(student):
        return ErrorResponse(
            code=ResponseCode.BAD_REQUEST,
            message="参数校验失败",
            errors={"name": "姓名格式不正确"}
        )
    # ... 创建逻辑
```

#### 异常捕获
```python
@router.get("/students")
async def get_students():
    try:
        students = get_all_students_from_db()
        return ListResponse(items=students, total=len(students))
    except Exception as e:
        return error(
            message=f"查询失败: {str(e)}",
            code=ResponseCode.INTERNAL_SERVER_ERROR
        )
```

### 4. 使用辅助函数

```python
from app.scheme.common_response import success, success_list, success_page, error

# 成功响应
return success(data=student, message="查询成功")

# 列表响应
return success_list(items=students, total=len(students))

# 分页响应
return success_page(
    items=students,
    total=100,
    page=1,
    page_size=10
)

# 错误响应
return error(message="操作失败", code=ResponseCode.BAD_REQUEST)
```

### 5. 状态码常量

```python
from app.scheme.common_response import ResponseCode

ResponseCode.SUCCESS               # 200
ResponseCode.CREATED              # 201
ResponseCode.NO_CONTENT           # 204
ResponseCode.BAD_REQUEST          # 400
ResponseCode.UNAUTHORIZED         # 401
ResponseCode.FORBIDDEN            # 403
ResponseCode.NOT_FOUND            # 404
ResponseCode.VALIDATION_ERROR     # 422
ResponseCode.INTERNAL_SERVER_ERROR # 500
```

### 6. 完整示例

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.scheme.common_response import ApiResponse, PageResponse, ResponseCode
from app.scheme.students_request import StudentsRequest

router = APIRouter(prefix="/students", tags=["学生管理"])

@router.post("/", response_model=ApiResponse)
async def create_student(
    student: StudentsRequest,
    db: Session = Depends(get_db)
):
    """创建学生"""
    try:
        new_student = create_student_in_db(db, student)
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

@router.get("/", response_model=PageResponse)
async def get_students(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """分页查询学生"""
    try:
        result = get_students_paginated(db, page, page_size)
        return PageResponse(
            items=result["items"],
            total=result["total"],
            page=page,
            page_size=page_size
        )
    except Exception as e:
        return error(
            message=f"查询失败: {str(e)}",
            code=ResponseCode.INTERNAL_SERVER_ERROR
        )

@router.get("/{s_id}", response_model=ApiResponse)
async def get_student(s_id: int, db: Session = Depends(get_db)):
    """查询单个学生"""
    student = get_student_from_db(db, s_id)
    if not student:
        raise HTTPException(
            status_code=ResponseCode.NOT_FOUND,
            detail="学生不存在"
        )
    return ApiResponse(data=student, message="查询成功")
```

## 响应格式

所有响应都遵循统一的格式：

```json
{
    "code": 200,
    "message": "操作成功",
    "data": { ... }      // ApiResponse 和 DetailResponse
    // 或
    "items": [ ... ],    // ListResponse 和 PageResponse
    "total": 100         // ListResponse 和 PageResponse
}
```

分页响应额外包含：
```json
{
    "page": 1,
    "page_size": 10,
    "total_pages": 10
}
```

## 下一步

- 查看 `app/scheme/README.md` 了解更多详细信息
- 查看 `app/api/response_example.py` 了解完整示例
- 查看 `app/tests/test_response_example.py` 了解测试方法

## 常见问题

### Q: 什么时候用 ApiResponse，什么时候用 DetailResponse？
A: `ApiResponse` 适用于返回单个对象，`DetailResponse` 适用于返回对象的详细信息。两者功能类似，主要在语义上有所区别。

### Q: PageResponse 的 total_pages 会自动计算吗？
A: 是的，PageResponse 会根据 total 和 page_size 自动计算 total_pages。

### Q: 如何在异常处理中使用统一响应类？
A: 使用 `error()` 辅助函数，或直接返回 `ErrorResponse` 对象。

### Q: 可以不指定泛型类型吗？
A: 可以，但建议指定以获得更好的类型提示和代码提示。
