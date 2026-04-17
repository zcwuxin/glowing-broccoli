from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.model.classes import Classes
from app.model.students import Students
from app.model.teachers import Teachers
from app.scheme.students_request import StudentsRequest
from sqlalchemy import func
from typing import List
from app.model.grades import Grades
from app.model.offers import Offers

# ====================== 更新学生 ======================
def update_student(db: Session, s_id: int, student: StudentsRequest):
    # ✅ 正确写法：从数据库查询学生
    db_student = db.query(Students).filter(Students.s_id == s_id, Students.s_isdel == 0).first()

    if not db_student:
        return None

    update_data = student.dict(exclude_unset=True)

    # 清理无效数据
    def clean_data(data):
        cleaned = {}
        for k, v in data.items():
            if v is None:
                continue
            if isinstance(v, str) and v.strip() in ["", "string"]:
                continue
            if isinstance(v, int) and v == 0 and k != "s_gender":
                continue
            cleaned[k] = v
        return cleaned

    update_data = clean_data(update_data)

    # 更新字段
    for k, v in update_data.items():
        setattr(db_student, k, v)

    db.commit()
    db.refresh(db_student)
    return db_student


# ====================== 逻辑删除 ======================
def delete_student(db: Session, s_id: int):
    # 先查询学生是否存在（未删除）
    student = db.query(Students).filter(
        Students.s_id == s_id,
        Students.s_isdel == 0
    ).first()

    # 如果不存在，直接返回 False
    if not student:
        return False

    # 存在
    db.query(Grades).filter(Grades.s_id == s_id).update({Grades.g_isdel: 1})
    db.query(Offers).filter(Offers.s_id == s_id).update({Offers.o_isdel: 1})
    db.query(Students).filter(Students.s_id == s_id).update({Students.s_isdel: 1})

    db.commit()
    return True


# ====================== 30岁以上学生 ======================
def get_students_over_30(db: Session):
    return db.query(Students).filter(Students.s_age > 30, Students.s_isdel == 0).all()


# ====================== 统计人数 ======================
def get_count(db: Session):
    total_user = db.query(func.count(Students.s_id)).filter(Students.s_isdel == 0).scalar()

    gender_query = db.query(
        Students.s_gender,
        func.count(Students.s_id)
    ).filter(
        Students.s_isdel == 0,
        Students.s_gender.isnot(None)
    ).group_by(Students.s_gender).all()

    gender_count = {}
    for gender, count in gender_query:
        key = "男" if gender == "男" else "女" if gender == "女" else f"未知({gender})"
        gender_count[key] = count

    return {
        "学生总数": total_user,
        "男女学生人数": gender_count
    }
def post_student(
        db: Session,
        student_req: StudentsRequest
    ) -> Students:  #函数执行完毕返回一个Students类型


    print('*' * 10 + ' [DAO] 执行 post_student')

    # 检查班级是否存在
    class_info = db.query(Classes).filter(
        Classes.c_id == student_req.c_id,
        Classes.c_isdel == 0
    ).first()

    teacher_info=db.query(Teachers).filter(
        Teachers.t_id == student_req.sales_id,
        Teachers.t_isdel == 0
    ).first()

    # 如果班级不存在
    if not class_info:
        raise HTTPException(
            status_code=400,
            detail=f"班级 ID {student_req.c_id} 不存在或已被删除"
        )

    if not teacher_info:
        raise HTTPException(
            status_code=400,
            detail=f"班级 ID {student_req.sales_id} 不存在或已被删除"
        )
    # 存在  将 Pydantic 模型转换为字典，
    student_data = student_req.dict()


    # 确保 s_id 不在插入列表中
    if 's_id' in student_data:
        del student_data['s_id']

        # 如果 s_del 没有默认值，手动设置一下防止 NULL
    if 's_isdel' not in student_data or student_data['s_isdel'] is None:
        student_data['s_isdel'] = 0

    #字典解包
    #1. 语法含义：** 是什么？在 Python 函数调用中，** 操作符的作用是：
                # 将一个字典（dict）的键值对，“展开”成函数的关键字参数
    #将student_data里面的键值对，展开成函数的关键字参数
    # student_data 是一个字典，来自 Pydantic模型的.dict()
    #Students(**student_data) 的执行过程： Python 会把字典里的每一个键值对，变成构造函数的参数：
    # 等价于执行了：
    # db_student = Students(
    #     c_id=1,
    #     s_name="张三",
    #     s_home="北京",
    #     s_age=20,
    #     ...
    # )
    #这样，SQLAlchemy 就会创建一个内存中的 Students 对象，并且每个属性赋值
    db_student = Students(**student_data)

    try:
        db.add(db_student)
        db.commit()  # 提交事务
        db.refresh(db_student)  # 刷新以获取数据库生成的 ID 和其他默认值
        return db_student
    except Exception as e:
        db.rollback()  # 出错回滚
        raise e

#多条件组合查询学生
def get_students(
        db: Session,
        query_params: dict  # 接收一个包含所有可选参数的字典，方便动态处理
) -> List[Students]:      #函数执行完毕会返回一个   List[Students] 类型

    print('*' * 10 + ' [DAO] 执行 get_students')

    query = db.query(Students)
    print(f'*' * 10 + ' [DAO] 执行 db.query(Students):{query}')

    # 条件匹配
    if query_params.get('s_id') is not None:
        query = query.filter(Students.s_id == query_params['s_id'])

    if query_params.get('c_id') is not None:
        query = query.filter(Students.c_id == query_params['c_id'])

    if query_params.get('s_college') is not None:
        query = query.filter(Students.s_college == query_params['s_college'])

    if query_params.get('s_major') is not None:
        query = query.filter(Students.s_major == query_params['s_major'])

    if query_params.get('s_academic') is not None:
        query = query.filter(Students.s_academic == query_params['s_academic'])

    if query_params.get('sales_id') is not None:
        query = query.filter(Students.sales_id == query_params['sales_id'])

    if query_params.get('s_gender') is not None:
        query = query.filter(Students.s_gender == query_params['s_gender'])

    # 模糊匹配
    if query_params.get('s_name'):
        # like("%xxx%") 表示包含 xxx
        query = query.filter(Students.s_name.like(f"%{query_params['s_name']}%"))

    if query_params.get('s_home'):
        # 籍贯模糊匹配
        query = query.filter(Students.s_home.like(f"%{query_params['s_home']}%"))

    #时间范围判断
    # start_date = query_params.get('s_study_date_start')
    # end_date = query_params.get('s_study_date_end')
    # print(f'------------打印开始时间：{start_date},{type(start_date)}')
    # print(f'------------打印结束时间：{end_date},{type(end_date)}')
    if query_params.get('s_study_date_start') is not None:
        query = query.filter(Students.s_study_date >= query_params.get('s_study_date_start'))

    if query_params.get('s_study_date_end') is not None:
        query = query.filter(Students.s_study_date <= query_params.get('s_study_date_end'))

    if  query_params.get('s_graduate_date_before') is not None:  #毕业时间之前
        query = query.filter(Students.s_graduate_date <= query_params.get('s_graduate_date_before'))

    if  query_params.get('s_graduate_date_after') is not None:  #毕业时间之前
        query = query.filter(Students.s_graduate_date >= query_params.get('s_graduate_date_after'))


    # 年龄范围判断
    age_min = query_params.get('s_age_min')
    age_max = query_params.get('s_age_max')

    if age_min is not None:
        query = query.filter(Students.s_age >= age_min)

    if age_max is not None:
        query = query.filter(Students.s_age <= age_max)

    # 删除标记过滤
    # 默认只查未删除的 (s_del=0)，除非明确指定查已删除的
    s_isdel = query_params.get('s_isdel', 0)
    query = query.filter(Students.s_isdel == s_isdel)

    # 执行查询并返回结果列表
    print(f'打印了query.all:{query.all()}')
    #打印了query.all:<model.students.Students object at 0x0000023EFEA5FE00>
    # 这里返回的是一个Students对象的lIST集合
    # [<model.students.Students object at 0x0000023EFEA5FE00>,
    # <model.students.Students object at 0x0000023EFEA5FE00>...]
    return query.all()
