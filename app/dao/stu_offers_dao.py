from sqlalchemy.orm import Session
from app.model.offers import Offers
from app.model.students import Students
from app.model.classes import Classes
from sqlalchemy import func,and_
from datetime import datetime
from typing import Optional
#按照学⽣编号，公司名字，⼯资范围查询学⽣就业信息
def get_stu_o_info(db:Session,s_id:int=None,o_company:str=None,min_salary:float=None,max_salary:float=None):
    query=db.query(Offers).filter(Offers.o_isdel==0)#这里的query始终都是对象
    if (s_id ==None and o_company==None and min_salary==None and max_salary==None):
        return query.all()
    if s_id is not None:
        query=query.filter(Offers.s_id==s_id)
    if o_company is not None:
        query=query.filter(Offers.o_company==o_company)
    if min_salary is not None:
        query=query.filter(Offers.o_salary>=min_salary)
    if max_salary is not None:
        query=query.filter(Offers.o_salary<=max_salary)
    return query.all()
#增加学生相关信息
def add__stu_o_info(db:Session,
                    s_id:int=None,
                    o_company:str=None,
                    o_salary:float=None,
                    o_open_date:datetime=None,
                    o_send_date:datetime=None):
    new_info=Offers(s_id=s_id,o_company=o_company,o_salary=o_salary,o_open_date=o_open_date,o_send_date=o_send_date,o_isdel=0)
    db.add(new_info)
    db.commit()
    db.refresh(new_info)
    return new_info
#删除学生信息(逻辑删,只能根据o_id来删，要不容易多删)
def del_stu_o_info_api(
        db:Session,
        o_id:int):
    query=db.query(Offers).filter(Offers.o_id==o_id, Offers.o_isdel == 0)
    try:
        updated_count = query.update({Offers.o_isdel: 1})
        db.commit()
        if updated_count > 0:
            return {"code": 200, "message": f"删除成功，影响 {updated_count} 条记录"}
        else:
            return {"code": 404, "message": "未找到匹配的记录"}
    except Exception as e:
        db.rollback()
        return {"code": 500, "message": f"删除失败: {str(e)}"}
# 修改学生信息
def stu_o_info_alter(db:Session,
                     o_id:int,
                     s_id:Optional[int]=None,
                     o_company:Optional[str]=None,
                     o_salary: Optional[float] = None,
                     o_open_date: Optional[datetime] = None,
                     o_send_date: Optional[datetime] = None):
    stu_alter_all=db.query(Offers).filter(Offers.o_isdel==0,Offers.o_id==o_id).first()
    if not stu_alter_all:
        return {"code": 404, "message": "未找到该条记录或已被删除"}
    if s_id is not None:
        stu_alter_all.s_id=s_id
    if o_company is not None:
        stu_alter_all.o_company=o_company
    if o_salary is not None:
        stu_alter_all.o_salary=o_salary
    if o_open_date is not None:
        stu_alter_all.o_open_date=o_open_date
    if o_send_date is not None:
        stu_alter_all.o_send_date=o_send_date
    try:
        db.commit()
        db.refresh(stu_alter_all)
        return {"code": 200, "message": "修改成功", "data": stu_alter_all}
    except Exception as e:
        db.rollback()
        return {"code": 500, "message": f"修改失败{e}"}

###获取班级就业人数
def get_class_o_info(db: Session, c_id: int = None):
    query = db.query(
        Classes.c_id,
        func.count(func.distinct(Students.s_id)).label("employment_count")
    ).outerjoin(
        Students,
        and_(
            Classes.c_id == Students.c_id,
            Students.s_isdel == 0
        )
    ).outerjoin(
        Offers,
        and_(
            Students.s_id == Offers.s_id,
            Offers.o_isdel == 0,
            Offers.o_send_date.isnot(None)
        )
    ).filter(
        Classes.c_isdel == 0
    )
    if c_id is not None:
        query = query.filter(Classes.c_id == c_id)
    result = query.group_by(Classes.c_id).all()
    return result
#############################获取班级就业人数饼状图
def get_class_pie_chart_data(db: Session, c_id: int = None):
    raw_data = get_class_o_info(db, c_id)
    if not raw_data:
        return {"series": [], "legend": []}
    pie_data = []
    legend_data = []
    for item in raw_data:
        class_name = f"班级{item.c_id}"
        count = int(item.employment_count or 0)
        pie_data.append({"name": class_name, "value": count})
        legend_data.append(class_name)
    return {
        "series": pie_data,       # 饼图数据
        "legend": legend_data,    # 图例
        "title": "各班级就业人数分布"
    }

###统计每个班级的平均就业时⻓（只统计进⼊就业阶段的学⽣，也就是有就业开放时间）
def class_acmulate_time(db: Session, c_id: int):
    try:
        query = db.query(
            Classes.c_id,
            func.avg(
                func.datediff(
                    Offers.o_send_date,
                    Offers.o_open_date
                )
            ).label("avg_days")
        ).outerjoin(
            Students,
            and_(
                Classes.c_id == Students.c_id,
                Students.s_isdel == 0
            )
        ).outerjoin(
            Offers,
            and_(
                Students.s_id == Offers.s_id,
                Offers.o_isdel == 0,
                Offers.o_open_date.isnot(None),
                Offers.o_send_date.isnot(None)
            )
        ).filter(
            Classes.c_isdel == 0
        )
        if c_id is not None:
            query = query.filter(Classes.c_id == c_id)

        result = query.group_by(Classes.c_id).all()
        return result

    except Exception as e:
        print("查询错误：", str(e))
        return None

##############################每个班级的平均就业时⻓(柱状图)
def get_class_chart_data(db: Session, c_id: int = None):
    raw_result = class_acmulate_time(db, c_id)
    if not raw_result:
        return {
            "x_data": [],
            "y_data": []
        }
    x_data = []
    y_data = []
    for row in raw_result:
        x_data.append(str(row.c_id))  # X轴：班级ID
        y_data.append(float(row.avg_days or 0))  # Y轴：平均天数（空值=0）
    return {
        "x_data": x_data,
        "y_data": y_data,
        "title": "班级平均处理时长",
        "x_name": "班级ID",
        "y_name": "平均天数（天）"
    }



