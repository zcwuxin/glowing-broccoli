from ..model.classes import Classes
from ..model.teachers import Teachers
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from ..model.students import Students


# ============= 班级数据操作 ==============

# 查询所有班级
def get_all_classes(db: Session):
    classes_list = db.query(Classes).filter(Classes.c_isdel==0).all()
    result = []
    for cls in classes_list:
        result.append({
        "c_id": cls.c_id,
        "c_name": cls.c_name,
        "c_start_date": cls.c_start_date,
        "c_isdel": cls.c_isdel,
        # 班主任（直接点出来）
        "homeroom_teacher": cls.homeroom_teacher.t_name if cls.homeroom_teacher else None,
        # 主讲老师（直接点出来）
        "lead_teacher": cls.lead_teacher.t_name if cls.lead_teacher else None,
    })
    return result

# 根据班级id查询单个班级信息
def get_class_by_id(db:Session,class_id:int):
    # 查询单个班级信息
    class_single = db.query(Classes).filter(Classes.c_id == class_id,Classes.c_isdel==0).first()
    if not class_single :
        return class_single
    # 把查询到的信息变成字典返回
    result = {
            "c_id": class_single.c_id,
            "c_name": class_single.c_name,
            "c_start_date":class_single.c_start_date,
            "c_isdel": class_single.c_isdel,
            # 班主任（直接点出来）
            "homeroom_teacher": class_single.homeroom_teacher.t_name if class_single.homeroom_teacher else None,
            # 主讲老师（直接点出来）
            "lead_teacher": class_single.lead_teacher.t_name if class_single.lead_teacher else None,
        }
    return result


# 分页查询班级信息
def get_class_by_page(db:Session,page_num,page_size):
    classes_list = (db.query(Classes).filter(Classes.c_isdel==0).order_by(Classes.c_id)
              .limit(page_size).offset((page_num - 1) * page_size).all())
    result = []
    for cls in classes_list:
        result.append({
            "c_id": cls.c_id,
            "c_name": cls.c_name,
            "c_start_date": cls.c_start_date,
            "c_isdel": cls.c_isdel,
            # 班主任（直接点出来）
            "homeroom_teacher": cls.homeroom_teacher.t_name if cls.homeroom_teacher else None,
            # 主讲老师（直接点出来）
            "lead_teacher": cls.lead_teacher.t_name if cls.lead_teacher else None,
        })
    return result

# 创建新的班级信息
def create_class(db:Session,class_data):
    from datetime import datetime
    # 日期转换
    start_date = datetime.strptime(class_data["c_start_date"], "%Y-%m-%d").date()

    # 存入数据库
    db_class = Classes(
        c_name=class_data["c_name"],
        c_start_date=start_date,
        homeroom_teacher_id=class_data['homeroom_teacher_id'],
        lead_teacher_id=class_data['lead_teacher_id'],
        c_isdel=0
    )
    # 把创建的班级信息添加到数据库
    db.add(db_class)
    # 提交事务
    db.commit()
    # 刷新数据
    db.refresh(db_class)
    # 返回创建的班级信息
    return db_class

# 更新班级信息
def update_class(db: Session, db_class: Classes, class_update: dict):
    from datetime import datetime

    for key, value in class_update.items():
        if value is None:
            continue  # 跳过空值，不覆盖原有数据

        # 日期字段单独处理
        if key == "c_start_date" and value != "":
            value = datetime.strptime(value, "%Y-%m-%d").date()

        # 动态赋值
        setattr(db_class, key, value)
    # 提交事务
    db.commit()
    # 刷新数据
    db.refresh(db_class)
    # 返回更新后的班级所有数据
    return db_class


# 删除班级
def delete_class(db:Session,class_id:int):
    # 输入班级id去Class类里查询是否存在
    db_class = db.query(Classes).filter(Classes.c_id == class_id,Classes.c_isdel==0).first()
    # 如果班级id不存在在返回None,否则更新c_isdel字段对应值为1，代表已删除
    if not db_class:
        return None
    db_class.c_isdel = 1
    for student in db_class.students:
        student.s_isdel = 1
    # 提交事务
    db.commit()
    # 刷新对象
    db.refresh(db_class)
    return db_class