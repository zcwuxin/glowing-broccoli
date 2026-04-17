from sqlalchemy import func, case
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import date

# 导入 ORM 模型
# from model.students import Students
# # 导入 Pydantic 请求模型 (用于新增)
# from schema.students_response import StudentsResponse
# from schema.students_request import StudentsRequest
# from schema.students_request import StudentsQueryRequest
# from model.classes import Classes


# 查询所有超过指定年龄的学生信息
from app.model.classes import Classes
from app.model.grades import Grades
from app.model.students import Students


def query_students_over_age(
        db: Session,  # 数据库会话
        age: int = 30  # 年龄阈值（默认30岁）
) -> List[Students]:  # 返回学生列表

    print('*' * 10 + ' [DAO] 执行 query_students_over_age')

    # 筛选年龄大于等于指定值且未删除的学生
    result = db.query(Students).filter(
        Students.s_age >= age,
        Students.s_isdel == 0
    ).all()

    print(f"查询到 {len(result)} 名超过 {age} 岁的学生")
    return result


# 统计每个班级的⼈数以及男⽣⼥⽣的⼈数
# 与班级表连表查询
"""
    统计每个班级的人数以及男女生人数
    使用 SQL 的 CASE WHEN 进行条件计数

"""


def query_class_gender_statistics(
        db: Session
) -> List[Tuple]:  # 这个函数返回一个列表，列表中的每个元素都是一个元组。

    print('*' * 10 + ' [DAO] 执行 query_class_gender_statistics')

    # 使用 case 表达式进行条件计数
    result = db.query(
        Classes.c_id,
        Classes.c_name,
        func.count(Students.s_id).label('total_count'),
        # 统计男生：s_gender == 1
        func.sum(
            case((Students.s_gender == '男', 1), else_=0)
        ).label('male_count'),
        # 统计女生：s_gender == 0
        func.sum(
            # CASE
            #     WHEN students.s_gender = 1 THEN 0
            #     ELSE 0
            # END

            case((Students.s_gender == '女', 1), else_=0)
        ).label('female_count')
    ).join(
        Students, Classes.c_id == Students.c_id  # 连表查询
    ).filter(
        Classes.c_isdel == 0,  # 班级未删除
        Students.s_isdel == 0  # 学生未删除
    ).group_by(
        Classes.c_id  # 按班级分组
    ).order_by(
        Classes.c_id  # 按班级ID排序
    ).all()
    print(f"统计了 {len(result)} 个班级的男女生人数")
    return result






#查询 查询有两次以上不及格的学⽣的姓名，班级和不及格成绩
def query_students_multiple_fails(
        db: Session,
        score: float = 60,
        count_score: int = 2
) -> List[dict]:
    ''''
    select
        students.s_id,
        studnets.s_name,
        grades.classes.c_id,
        grades.g_order,
        grades.scores
    from students
    join students on students.s_id=grades.s_id
    join classes  on students.c_id=classes.c_id
    where students.s_id in (
        select  distinct s_id
        from grades
        where grades.分数< 【指定分数】
        group by grades.s_id
        having count(g_order)>【指定次数】
        ) and studnets.s_isdel=0 and grades.g_isdel=0 and classes.c_isdel=0;
    '''
    print('*' * 10 + '[DAO] 执行 query_students_multiple_fails')

    #子查询
    grades_s_id=db.query(Grades.s_id).\
        filter(Grades.g_score<score,Grades.g_isdel==0).\
        group_by(Grades.s_id).\
        having(func.count(Grades.g_order)>=count_score)\
        .subquery()


    res=db.query(Students.s_id.label('s_id'),
                 Students.s_name.label('s_name'),
                 Classes.c_id.label('c_id'),
                 Classes.c_name.label('c_name'),
                 Grades.g_order.label('g_order'),
                 Grades.g_score.label('g_score')).\
        join(Grades,Students.s_id==Grades.s_id).\
        join(Classes,Classes.c_id==Students.c_id).\
        filter(Students.s_id.in_(grades_s_id)
               ,Students.s_isdel==0
               ,Classes.c_isdel==0
               ,Grades.g_isdel==0
               ). \
        order_by(Students.s_id, Grades.g_order.asc()). \
        all()
    # {学生ID: 学生信息字典}
    student_map = {}
    for row in res:
        s_id = row.s_id
        #学号：数据
        # 如果该学生还没在字典里，初始化结构
        if s_id not in student_map:
            student_map[s_id] = {
                's_id': row.s_id,
                's_name': row.s_name,
                'c_id': row.c_id,
                'c_name': row.c_name,
                'g_order_count': []  # 初始化成绩列表
            }
            # 将当前行的成绩添加到该学生的列表中
        student_map[s_id]['g_order_count'].append({
            'g_order': row.g_order,
            'g_score': row.g_score
        })
    result = list(student_map.values())
    print(f'================{result}')
    return result




"""
    统计每次考试每个班级的平均分
    返回按平均分从高到低排序的结果
"""

def query_class_avg_score(
        db: Session
) -> List[dict]:

    print('*' * 10 + '[DAO] 执行 query_class_avg_score')

    results = db.query(
        Grades.g_order.label('g_order'),
        Classes.c_id.label('c_id'),
        Classes.c_name.label('c_name'),
        func.avg(Grades.g_score).label('class_avg_score')
    ).join(
        Students, Grades.s_id == Students.s_id
    ).join(
        Classes, Students.c_id == Classes.c_id
    ).filter(
        Grades.g_isdel == 0,
        Students.s_isdel == 0,
        Classes.c_isdel == 0
    ).group_by(
        Classes.c_id,  #先按班级名字分
        Grades.g_order,  #再按每个班级每次考试次序分
        Classes.c_name
    ).order_by(
        Classes.c_name,  #先按班级排序，班级排序之后
        func.avg(Grades.g_score).desc() # 再按班级每次考试的分数排序
    ).all()


    response_map = {}
    #
    for row in results:
        c_id=row.c_id
        if c_id not in response_map:
            response_map[c_id] = {
                "c_id": row.c_id,
                "c_name":row.c_name,
                "avg_score_count":[]
            }
        response_map[c_id]['avg_score_count'].append({
            'g_order': row.g_order,
            'class_avg_score': row.class_avg_score
        })

    res_student=list(response_map.values())
    print(f"统计了 {len(res_student)} 条考试-班级平均分记录")
    return res_student