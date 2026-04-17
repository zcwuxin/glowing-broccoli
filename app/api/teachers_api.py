from fastapi import APIRouter, Depends, Query, Path, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from app.dao.teachers_dao import get_teachers_all, add_teacher, get_specific_teachers, update_specific_teacher, \
    delete_specific_teacher
from app.model.classes import Classes
from app.model.teachers import Teachers
from app.scheme.teachers_scheme import TeachersDB, TeachersResponse, TeachersRegisterResponse, \
    TeachersRegisterRequest, TeachersSearchRequest, TeacherUpdateRequest, ClassesResponse

security = HTTPBearer()
router = APIRouter()


def to_classes(classes: Classes) -> ClassesResponse:
    return ClassesResponse(
        c_id=classes.c_id,
        c_name=classes.c_name,
    )


def to_teachers_db(teacher: Teachers) -> TeachersDB:
    return TeachersDB(
        t_id=teacher.t_id,
        t_name=teacher.t_name,
        t_gender=teacher.t_gender,
        t_home_classes=[ClassesResponse(c_id=c.c_id, c_name=c.c_name) for c in teacher.homeroom_classes],
        t_lead_classes=[ClassesResponse(c_id=c.c_id, c_name=c.c_name) for c in teacher.lead_classes],
        # roles=[TeachersRolesResponse(r_id=r.r_id, r_name=r.r_name) for r in teacher.roles],
        t_hire_date=teacher.t_hire_date
    )

# # 查询所有老师信息
# @router.get("/teachers", response_model=TeachersResponse)
# async def get_teachers(db=Depends(get_db)):
#     try:
#         # 调用teachers_dao查询所有老师信息
#         teachers_db = get_teachers_all(db)
#         print("查询结果:", teachers_db)
#         data = [to_teachers_db(t) for t in teachers_db]
#         print("data", data)
#         # 添加查询结果到响应体模型
#         return TeachersResponse(code=200, message="查询成功", data=data)
#     except Exception as e:
#         print("*查询所有老师报错：", e)
#         raise HTTPException(status_code=500, detail="*查询过程报错")


# 更新指定ID老师基本信息
@router.put("/teachers/{t_id}", response_model=TeachersRegisterResponse,summary='修改老师信息')
async def update_expr_teacher(req: TeacherUpdateRequest, db=Depends(get_db), t_id: int = Path(..., description="更新指定ID老师信息"),credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        teachers_db = update_specific_teacher(req, db, t_id)
        if teachers_db:
            data = to_teachers_db(teachers_db)
            return TeachersRegisterResponse(code=200, message="更新成功", data=data)
    except HTTPException as e:
        db.rollback()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print("*更新老师信息错误：", e)
        db.rollback()
        raise HTTPException(status_code=500, detail="*更新失败")

# 删除指定ID老师
@router.delete("/teachers/{t_id}", response_model=TeachersRegisterResponse,summary='删除老师信息')
async def delete_teacher(t_id: int = Path(..., description="删除指定ID的老师"), db=Depends(get_db),
                         credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        teachers_db = delete_specific_teacher(t_id, db)
        if teachers_db:
            print("teachers_db", teachers_db)
            data = to_teachers_db(teachers_db)
            return TeachersRegisterResponse(code=200, message="删除成功", data=data)
    except HTTPException as e:
        db.rollback()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print("*筛选条件查询错误：", e)
        db.rollback()
        raise HTTPException(status_code=500, detail="*删除失败")

# 创建老师基本信息
@router.post("/teachers", response_model=TeachersRegisterResponse,summary='添加老师信息',)
async def register_teacher(req: TeachersRegisterRequest, db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # 调用teachers_dao验证并增加新老师信息
        res = add_teacher(req, db)
        if res:
            data = to_teachers_db(res)
            return TeachersRegisterResponse(code=200, message="添加成功", data=data)
    except HTTPException as e:
        db.rollback()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        db.rollback()
        print("*添加新老师错误：", e)
        raise HTTPException(status_code=500, detail="*添加失败")

# 根据筛选条件查询老师信息
@router.get("/teachers", response_model=TeachersResponse,summary='查询老师信息')
async def get_expr_teachers(req: TeachersSearchRequest=Depends(), db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        teachers_db = get_specific_teachers(req, db)
        data = [to_teachers_db(t) for t in teachers_db]
        return TeachersResponse(code=200, message="查询成功", data=data)
    except Exception as e:
        print("筛选条件查询错误：", e)
        raise HTTPException(status_code=500, detail="*查询失败")
