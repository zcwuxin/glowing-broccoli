from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.model.classes import Classes
from app.model.teachers import Teachers
from app.scheme.teachers_scheme import TeachersRegisterRequest, TeachersSearchRequest, TeacherUpdateRequest


# 查询所有老师信息
def get_teachers_all(db: Session):
    teachers_db = db.query(Teachers).filter(Teachers.t_isdel == 0).all()
    print("teachers_db:", teachers_db)
    return teachers_db


# 添加新老师信息
def add_teacher(teacher_req: TeachersRegisterRequest, db: Session):
    # 检查是否输入班级编号
    # if teacher_req.c_id:
    #     # 若有输入，则检查班级编号是否存在
    #     class_id = db.query(Classes).filter(Classes.c_id == teacher_req.c_id).first()
    #     if not class_id:
    #         raise HTTPException(status_code=404, detail="*无该班级编号")
    # t_roles_list = []
    # # 老师角色生成角色列表
    # for each in teacher_req.roles:
    #     this_role = db.query(TeacherRole).filter(TeacherRole.r_name == each.value).first()
    #     if not this_role:
    #         raise HTTPException(status_code=404, detail=f"角色 {each.value} 不存在")
    #     t_roles_list.append(this_role)
    # 添加新老师信息到数据库
    new_teacher = Teachers(t_name=teacher_req.t_name, t_gender=teacher_req.t_gender, t_hire_date=teacher_req.t_hire_date)
    db.add(new_teacher)
    db.commit()
    # 返回新老师的信息
    db.refresh(new_teacher)
    return new_teacher


# 查询指定筛选条件的老师信息
def get_specific_teachers(teacher_req: TeachersSearchRequest, db: Session):
    # 先从数据库中查询得到所有老师信息
    teachers_db = db.query(Teachers)
    # 去除逻辑删的老师
    teachers_db = teachers_db.filter(Teachers.t_isdel == 0)
    # 根据姓名
    if teacher_req.t_name:
        teachers_db = teachers_db.filter(Teachers.t_name.contains( teacher_req.t_name))
    # 根据性别
    if teacher_req.t_gender:
        teachers_db = teachers_db.filter(Teachers.t_gender == teacher_req.t_gender)
    # 根据开始入职日期
    if teacher_req.t_start_hire_date:
        teachers_db = teachers_db.filter(Teachers.t_hire_date >= teacher_req.t_start_hire_date)
    # 根据结束入职日期
    if teacher_req.t_end_hire_date:
        teachers_db = teachers_db.filter(Teachers.t_hire_date <= teacher_req.t_end_hire_date)
    # # 根据角色
    # if teacher_req.roles:
    #     # 查询老师的角色列表
    #     t_roles_list = [role.value for role in teacher_req.roles]
    #     # 查询匹配所有角色的老师，保证roles的数量和len(role_list)相等
    #     teachers_db = teachers_db.join(Teachers.roles).filter(
    #         TeacherRole.r_name.in_(t_roles_list)
    #     ).group_by(Teachers.t_id).having(
    #         func.count(TeacherRole.r_id.distinct()) == len(t_roles_list)
    #     )
    #     teachers_db = teachers_db.distinct()
    # 根据班级名
    if teacher_req.t_class_name:
        teachers_db = teachers_db.filter(
            or_(
                # 关联查询：老师担任的班级中，班级名称包含关键字
                Teachers.homeroom_classes.any(Classes.c_name.contains(teacher_req.t_class_name)),
                Teachers.lead_classes.any(Classes.c_name.contains(teacher_req.t_class_name))
            )
        ).distinct()
    # 去重
    teachers_db = teachers_db.distinct()
    # 根据t_id排序
    teachers_db = teachers_db.order_by(Teachers.t_id).all()
    return teachers_db


# 更新指定ID老师信息
def update_specific_teacher(teacher_req: TeacherUpdateRequest, db: Session, t_id: int):
    # 判断是否有该ID的老师
    this_teacher = db.query(Teachers).filter(Teachers.t_id == t_id, Teachers.t_isdel != 1).first()
    if not this_teacher:
        raise HTTPException(status_code=404, detail="*无该ID老师")
    # 更新老师基本信息
    # 根据姓名
    if teacher_req.t_name is not None:
        this_teacher.t_name = teacher_req.t_name or this_teacher.t_name
    # 根据性别
    if teacher_req.t_gender is not None:
        this_teacher.t_gender = teacher_req.t_gender or this_teacher.t_gender
    # 根据班级编号
    # if teacher_req.c_id is not None:
    #     this_cid = db.query(Classes).filter(Classes.c_id == teacher_req.c_id).first()
    #     if not this_cid:
    #         raise HTTPException(status_code=404, detail="无该班级编号")
    #     this_teacher.c_id = teacher_req.c_id
    # # 根据角色
    # if teacher_req.roles is not None:
    #     t_roles_list = []
    #     # 老师角色生成角色列表
    #     for each in teacher_req.roles:
    #         this_role = db.query(TeacherRole).filter(TeacherRole.r_name == each.value).first()
    #         if not this_role:
    #             raise HTTPException(status_code=404, detail=f"角色 {each.value} 不存在")
    #         t_roles_list.append(this_role)
    #     this_teacher.roles = t_roles_list
    # 根据入职时间
    if teacher_req.t_hire_date is not None:
        this_teacher.t_hire_date = teacher_req.t_hire_date or this_teacher.t_hire_date
    db.commit()
    db.refresh(this_teacher)
    return this_teacher


# 删除指定ID老师的信息
def delete_specific_teacher(t_id, db: Session):
    # 判断是否有该ID的老师
    this_teacher = db.query(Teachers).filter(Teachers.t_id == t_id, Teachers.t_isdel != 1).first()
    if not this_teacher:
        raise HTTPException(status_code=404, detail="*无该ID老师")
    # 逻辑删该ID的老师
    this_teacher.t_isdel = 1
    db.commit()
    db.refresh(this_teacher)
    return this_teacher

