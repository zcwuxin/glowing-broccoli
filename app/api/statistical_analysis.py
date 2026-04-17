import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from matplotlib import pyplot as plt
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from app.dao import grades_dao
from app.dao import stu_offers_dao

from app.core.database import get_db
from app.dao import students_dao, statistics_dao
from app.dao.statistical_analysis_dao import query_students_over_age, query_class_gender_statistics, \
    query_students_multiple_fails, query_class_avg_score
from app.model.classes import Classes
from app.model.students import Students
from app.scheme.statistics_response import ClassStatisticsResponse, ClassAvgScoreResponse, FailStudentResponse
from app.scheme.students_response import StudentsResponse

'''
统计分析模块

'''
statistical_analysis_router=APIRouter()
security = HTTPBearer()


@statistical_analysis_router.get(
    '/statistics/over_age',
    response_model=List[StudentsResponse],
    summary='查询所有超过X岁的学生信息'
)
async def get_students_over_age(
        age: int = Query(30, description="查询所有超过X岁的学生信息", ge=0),
        db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        from app.dao.statistical_analysis_dao import query_students_over_age
        students = query_students_over_age(db, age)
        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

#统计每个班级的人数及男女生人数
@statistical_analysis_router.get(
    '/statistics/gender_info',
    response_model=List[ClassStatisticsResponse],
    summary='统计每个班级的人数及男女生人数'
)
async def get_class_gender_statistics(
        db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)
):

    try:
        #这里返回的数据格式 List[Tuple]
        results = query_class_gender_statistics(db)

        # 将元组结果转换为字典格式  列表推导式
        response = [
            ClassStatisticsResponse(
                c_id=r[0],
                c_name=r[1],
                total_students=r[2],
                male_count=r[3],
                female_count=r[4]
            )
            for r in results
        ]


        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")




#查询有两次以上不及格的学⽣的姓名，班级和不及格成绩
@statistical_analysis_router.get(
    '/statistics/scores_count',
    response_model=List[FailStudentResponse],
    summary='查询X次不及格的学生姓名，班级及成绩'
)
async def get_studnets_fail_scores(
        db: Session = Depends(get_db),
        score: float = Query(60, description="分数阈值"),
        score_count:int=Query(2,description='考试次数'),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    try:
        res=query_students_multiple_fails(db,score,score_count)
        print('*'*80)
        # 转换为响应模型
        response_stu = [
            FailStudentResponse(
                s_id=item['s_id'],
                s_name=item['s_name'],
                c_id=item['c_id'],
                c_name=item['c_name'],
                g_order_count=item['g_order_count']
            )
            for item in res
        ]
        # print(res)

        return response_stu
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")


# statistical_analysis.py


"""
    统计每次考试每个班级的平均分
    结果按照平均分从高到低排序
"""
@statistical_analysis_router.get(
    '/statistics/class_avg_score',
    response_model=List[ClassAvgScoreResponse],
    summary='统计每次考试每个班级的平均分（按平均分从高到低排序）'
)
async def get_class_avg_score_by_exam(
        db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)
):

    try:
        results = query_class_avg_score(db)

        # 将字典转换为 Pydantic 模型
        #使用列表推导式
        response_stu = [
            ClassAvgScoreResponse(
                c_id=item["c_id"],
                c_name=item['c_name'],
                avg_score_count=item['avg_score_count']
            )
            for item in results
        ]

        return response_stu
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")



#=====================================================================================
#YJY
from fastapi.responses import Response
# ====================== 性别分布饼图 ======================
@statistical_analysis_router.get("/statistics/gender_sta", response_class=Response,summary='性别分布饼图')
async def get_student_count_chart(db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    data = students_dao.get_count(db)
    gender_data = data["男女学生人数"]

    labels = list(gender_data.keys())
    sizes = list(gender_data.values())
    colors = ["#FF6B6B", "#4DABF7", "#51CF66", "#FFD43B"]

    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(7, 7))

    def make_autopct(sizes):
        def my_autopct(pct):
            total = sum(sizes)
            val = int(round(pct * total / 100))
            return f'{pct:.1f}%\n({val}人)'
        return my_autopct

    ax.pie(
        sizes,
        labels=labels,
        autopct=make_autopct(sizes),
        colors=colors[:len(labels)],
        startangle=90,
        textprops={'fontsize': 12}
    )
    ax.set_title("学生性别分布", fontsize=16, pad=20)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return Response(content=buf.getvalue(), media_type="image/png")

####统计就业薪资最⾼的前五名学⽣的姓名，班级和就业时间(拿到offer的时间)，就业公司
@statistical_analysis_router.get('/statistics/employee_date',summary='统计就业薪资最⾼的前五名学⽣')
async def salary_top5(db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    return statistics_dao.top5_salary_students(db)

#####统计每个学⽣的就业时⻓（offer下发时间-就业开放时间)
@statistical_analysis_router.get('/statistics/offers_start',summary='统计每个学⽣的就业时⻓')
async def job_duration_days(db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = statistics_dao.student_job_duration(db)
    # 如果没有数据，返回明确提示，不会空白
    if not result:
        return {"code": 200, "msg": "暂无就业数据", "data": []}

    return {"code": 200, "msg": "查询成功", "data": result}
# 查询每次考试成绩都在xx分以上的学⽣的编号，姓名和成绩
@statistical_analysis_router.get('/statistics/grade_sta',response_model=None,summary='统计每次考试成绩都在xx分以上')
async def get_grade_sta1(score,db= Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    res = grades_dao.grade_sta1(db,score)
    if res:
        return f'"code":200,"message":{res}'
    else:
        raise HTTPException(status_code=404,detail="没有符合要求的学生")
# 查询有两次以上不及格的学⽣的姓名，班级和不及格成绩
# 统计每次考试每个班级的平均分，按照从⾼到低排序
##查询班级就业人数
@statistical_analysis_router.get("/statistics/employment_class/{c_id}", summary="查询指定班级的就业统计")
async def class_emp_acmulate(c_id: int, db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        result = stu_offers_dao.get_class_o_info(db, c_id=c_id)
        if result is None:
            return {"message": "查询异常，请联系管理员", "code": 500, "data": None}
        if not result:
            return {"message": "该班级暂无就业数据", "code": 404, "data": None}
        data = {
            "c_id": result[0][0],
            "employment_count": result[0][1]
        }
        return {
            "message": "查询成功",
            "code": 200,
            "data": data
        }
    except Exception as e:
        return {"message": f"服务器内部错误: {str(e)}", "code": 500, "data": None}
@statistical_analysis_router.get("/statistics/class_employment_pie",summary="查询班级就业人数(饼状图)")
#################查询班级就业人数饼状图
def class_employment_pie(c_id: int = None, db= Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    data = stu_offers_dao.get_class_pie_chart_data(db, c_id)
    return {
        "code": 200,
        "msg": "success",
        "data": data
    }



###统计每个班级的平均就业时⻓（只统计进⼊就业阶段的学⽣，也就是有就业开放时间）
@statistical_analysis_router.get("/statistics/classes_offers_time/{c_id}", summary="每个班级的平均就业时长")
async def avg_class_time(c_id: int, db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        res = stu_offers_dao.class_acmulate_time(db=db, c_id=c_id)
        if res is None:
            return {"message": "查询异常，请联系管理员", "code": 500, "data": None}
        if not res:
            return {"message": "该班级暂无就业数据", "code": 404, "data": None}
        data = {
            "c_id": res[0][0],
            "avg_days": float(res[0][1]) if res[0][1] else 0
        }
        return {
            "message": "查询成功",
            "code": 200,
            "data": data
        }
    except Exception as e:
        return {"message": f"服务器内部错误: {str(e)}", "code": 500, "data": None}
##############################每个班级的平均就业时⻓(柱状图)
@statistical_analysis_router.get("/statistics/employee_time",summary="每个班级的平均就业时⻓(柱状图)")
def class_time_chart(c_id: int = None, db = Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    chart_data = stu_offers_dao.get_class_chart_data(db, c_id)
    return {
        "code": 200,
        "msg": "success",
        "data": chart_data
    }


@statistical_analysis_router.get("/statistics/gender_info_json")
async def get_class_gender_statistics_json(
        db: Session = Depends(get_db)
):
    """返回班级性别统计的JSON数据"""
    from sqlalchemy import func, case

    # 方案1：直接从数据库查询
    results = db.query(
        Classes.c_id,
        Classes.c_name,
        func.count(Students.s_id).label('total_students'),
        func.sum(case((Students.s_gender == '男', 1), else_=0)).label('male_count'),
        func.sum(case((Students.s_gender == '女', 1), else_=0)).label('female_count')
    ).outerjoin(Students, Classes.c_id == Students.c_id) \
        .group_by(Classes.c_id, Classes.c_name).all()

    return [
        {
            "c_id": r.c_id,
            "c_name": r.c_name,
            "total_students": r.total_students or 0,
            "male_count": r.male_count or 0,
            "female_count": r.female_count or 0
        }
        for r in results
    ]


@statistical_analysis_router.get("/statistics/gender_sta", response_class=Response, summary='性别分布饼图')
async def get_student_count_chart(
        db: Session = Depends(get_db),
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """返回性别分布饼图（PNG图片）"""
    data = students_dao.get_count(db)
    gender_data = data["男女学生人数"]

    labels = list(gender_data.keys())
    sizes = list(gender_data.values())
    colors = ["#FF6B6B", "#4DABF7", "#51CF66", "#FFD43B"]

    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(7, 7))

    def make_autopct(sizes):
        def my_autopct(pct):
            total = sum(sizes)
            val = int(round(pct * total / 100))
            return f'{pct:.1f}%\n({val}人)'

        return my_autopct

    ax.pie(
        sizes,
        labels=labels,
        autopct=make_autopct(sizes),
        colors=colors[:len(labels)],
        startangle=90,
        textprops={'fontsize': 12}
    )
    ax.set_title("学生性别分布", fontsize=16, pad=20)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return Response(content=buf.getvalue(), media_type="image/png")
