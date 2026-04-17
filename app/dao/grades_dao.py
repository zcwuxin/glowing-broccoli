from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.model.grades import Grades
from app.model.students import Students



#查某个学生的某次成绩
def get_grade(db:Session,s_id:int,g_order:int):
    res=db.query(Grades.g_score).filter(Grades.s_id == s_id,Grades.g_order == g_order,Grades.g_isdel==0).first()
    return res


#为某个学生录入一条新成绩
def post_grade(db:Session,s_id:int,g_order:int,g_score:float):
    res =db.query(Grades.g_score).filter(Grades.s_id == s_id,Grades.g_order == g_order,Grades.g_isdel==0).all()
    #查出来如果有值，代表原本就有成绩了,在api里抛出报错即可
    if res:
        return 1
    #没有值，代表没成绩，才执行录入
    else:
        grades = Grades(s_id=s_id,g_order=g_order,g_score=g_score)
        db.add(grades)
        db.commit()
        return 0

#为某个学生修改成绩
def put_grade(db:Session,s_id:int,g_order:int,g_score:float):
    res =db.query(Grades).filter(Grades.s_id == s_id,Grades.g_order == g_order,Grades.g_isdel==0).first()
    #查出来如果有值，代表原本就有成绩了,直接改即可
    if res:
        res.g_score=g_score
        db.commit()
        return 1
    #没有值，代表没成绩，不可以改
    else:
        return 0

#删除学生的某次考试成绩
def remove_grade(db:Session,s_id:int,g_order:int):
    res =db.query(Grades).filter(Grades.s_id == s_id,Grades.g_order == g_order,Grades.g_isdel==0).first()
    #有值的话就直接删，把g_isdel改为1
    if res:
        res.g_isdel=1
        db.commit()
        return 1
    #没有值，则代表没成绩，没办法删
    else:
        return 0


#给grade/sta1接口用的
# 查询每次考试成绩都在80分以上的学⽣的编号，姓名和成绩
def grade_sta1(db:Session,score:float):
    subquery = db.query(Grades.s_id).filter(Grades.g_isdel==0).group_by(Grades.s_id).having(func.min(Grades.g_score)>=score).all()
    subquery_ls = [i[0] for i in subquery]
    print(subquery_ls)
    # query =db.query(Grades.s_id,Students.s_name,Grades.g_order,Grades.g_score).options(joinedload(Grades.students)).filter(Grades.g_isdel==0,Grades.s_id.not_in(subquery)).all()
    query =db.query(Grades,Students).options(joinedload(Grades.students)).filter(Grades.g_isdel==0,Grades.s_id==Students.s_id,Grades.s_id.in_(subquery_ls)).all()
    print(query)
    ls =[]
    for q in query:
        ls.append((q.Grades.s_id,q.Grades.students.s_name,q.Grades.g_order,q.Grades.g_score))
    print(ls)
    return ls





# def grade_fn1(db:Session,c_id:int,score:float,operator:str):
#     sql = 'select g.s_id,s.s_name ,g.g_order ,g.g_score from grades g,students s where g.s_id =s.s_id and g.is_del =0
#            and s.s_id in (select s_id from  grades where g.is_del =0 group by s_id having min(g_score)>=80)'
#     if c_id:
#         sql += " AND s.c_id = :c_id"
#     sql =sql.format(operator=operator)
#
#
#
# # 2. 如果传了班级，追加条件
#     if req.c_id is not None:
#         sql +=
#     if operator==">":