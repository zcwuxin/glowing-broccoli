from sqlalchemy.orm import Session
from ..model.offers import Offers
from ..model.students import Students
from ..model.classes import Classes

from sqlalchemy import func,text
from datetime import datetime
from typing import Optional

# ===========================================   2.6.3就业统计  =====================================

####统计就业薪资最⾼的前五名学⽣的姓名，班级和就业时间(拿到offer的时间)，就业公司
def top5_salary_students(db: Session):
    # 1. 计算排名
    rank_subquery = db.query(
        Offers.s_id,
        Offers.o_company,
        Offers.o_salary,
        Offers.o_send_date,
        func.dense_rank().over(order_by=Offers.o_salary.desc()).label("rn")
    ).filter(Offers.o_isdel == 0).subquery()

    # 2. 关联学生、班级
    result = db.query(
        Students.s_id,
        Students.s_name,
        Classes.c_id,
        Classes.c_name,
        rank_subquery.c.o_company,
        rank_subquery.c.o_salary,
        rank_subquery.c.o_send_date
    ).join(
        rank_subquery, Students.s_id == rank_subquery.c.s_id
    ).join(
        Classes, Classes.c_id == Students.c_id
    ).filter(
        rank_subquery.c.rn <= 5,
        Students.s_isdel == 0,
        Classes.c_isdel == 0
    ).order_by(rank_subquery.c.o_salary.desc()).all()

    # 把查询结果转成 字典列表！！！
    return [
        {
            "s_id": row.s_id,
            "s_name": row.s_name,
            "c_id": row.c_id,
            "c_name": row.c_name,
            "o_company": row.o_company,
            "o_salary": float(row.o_salary) if row.o_salary else 0,
            "o_send_date": row.o_send_date.strftime("%Y-%m-%d %H:%M:%S") if row.o_send_date else None
        }
        for row in result
    ]

#####统计每个学⽣的就业时⻓（offer下发时间-就业开放时间)
def student_job_duration(db: Session):
    # 计算 就业时长 = offer下发时间-就业开放时间（天数）
    duration_days = func.timestampdiff(
        text("day"),
        Offers.o_open_date,  # 就业开放时间
        Offers.o_send_date,  # offer下发时间（就业表）
    ).label("job_duration_days")
    # 连表查询
    result = db.query(Students.s_name,
                      Offers.o_open_date,
                      Offers.o_send_date,
                      Offers.o_company,
                      duration_days
                      ).join(Offers, Students.s_id == Offers.s_id).filter(Students.s_isdel==0).all()
    #  转成字典，防止 FastAPI 序列化报错
    return [
        {
            "s_name": row.s_name,
            "o_open_date": row.o_open_date.strftime("%Y-%m-%d %H:%M") if row.o_open_date else None,
            "o_send_date": row.o_send_date.strftime("%Y-%m-%d %H:%M") if row.o_send_date else None,
            "o_company": row.o_company,
            "job_duration_days": row.job_duration_days
        }
        for row in result
    ]