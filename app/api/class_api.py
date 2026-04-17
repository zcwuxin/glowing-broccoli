from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..dao.class_dao import get_all_classes,get_class_by_id,create_class,update_class,delete_class
from ..core.database import get_db
from fastapi import APIRouter, Depends, HTTPException,Form
from ..dao import class_dao
from ..model.classes import Classes
from ..model.teachers import Teachers

class_router = APIRouter()
security = HTTPBearer()

# ================= 班级接口 ====================

# 更新班级信息
@class_router.put('/classes/{class_id}',summary='更新班级信息')
async def edit_class(
    class_id: int,
    c_name: str = Form(None),
    c_start_date: str = Form(None),
    homeroom_teacher_id:int = Form(None,ge=1),
    lead_teacher_id:int = Form(None,ge=1),
    db = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # 组装成 class_update 键值对（只传有值的）
    class_update = {}
    if c_name is not None:
        class_update["c_name"] = c_name
    if c_start_date is not None:
        class_update["c_start_date"] = c_start_date
    if homeroom_teacher_id is not None:
        class_update["homeroom_teacher_id"] = homeroom_teacher_id
    if lead_teacher_id is not None:
        class_update["lead_teacher_id"] = lead_teacher_id

    # 查询班级是否存在，调用class_dao里的按字段查询班级函数get_class_by_id
    db_class = db.query(Classes).filter(Classes.c_id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="班级不存在")

    try:
        # 调用更新方法
        update_class(db, db_class, class_update)
        return db_class

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新失败：{str(e)}")

# 删除班级
@class_router.delete('/classes/{class_id}',summary='删除班级信息')
async def remove_class(class_id:int,db=Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    # 调用class_dao里的delete_class函数
    success = delete_class(db, class_id)
    if not success:
        raise HTTPException(status_code=404, detail="班级不存在，无法删除")
    return {"message": "删除成功",'isdel':success.c_isdel}

#  创建新班级
@class_router.post('/classes/',summary='添加班级信息')
async def add_class(
        c_name: str = Form(...),
        c_start_date: str = Form(...),
        homeroom_teacher_id:int = Form(...,ge=1),
        lead_teacher_id:int = Form(...,ge=1),
        db = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        # 判断老师存不存在
        teacher = db.query(Teachers).filter(Teachers.t_id == homeroom_teacher_id,Teachers.t_id == lead_teacher_id).first()
        if  teacher:
            raise HTTPException(status_code=400, detail="老师不存在")
        # 组装成 class_data 字典（键值对）
        class_data = {
            "c_name": c_name,
            "c_start_date": c_start_date,
            'homeroom_teacher_id':homeroom_teacher_id,
            'lead_teacher_id':lead_teacher_id
        }

        #调用class_dao.py的create_class函数
        result = create_class(db, class_data)
        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"添加失败：{str(e)}")

# 获取所有班级列表
@class_router.get('/classes',summary='查询班级信息')
async def list_classes(db=Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
     return get_all_classes(db)
