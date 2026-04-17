from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core import Base

# **2.4** 学生考核成绩表
#
# 成绩录⼊与管理
# 按考核序次录⼊考核成绩（ 成绩编号 g_id    学⽣编号 （外键）s_id、考核序次 g_order、成绩g_score）
#成绩表 ：学生表  -  > 1:n  的关系
#外键在成绩表这里，指向学生表
class Grades(Base):
    __tablename__ = "grades"
    g_id =Column(Integer,primary_key=True,autoincrement=True)      # 成绩编号  主键自增
    s_id= Column(Integer,ForeignKey('students.s_id'))          # 外键   指向学生s_id
    g_order=Column(Integer)                                      #考核次数
    g_score=Column(Float)                             #考核成绩
    g_isdel = Column(Integer,default=0)

    students=relationship('Students',back_populates='grades')    #与学生表建立联系


