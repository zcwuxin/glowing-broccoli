from sqlalchemy import Column, Integer, String,Date, ForeignKey
from sqlalchemy.orm import relationship

from app.core import Base

# 学⽣信息增改查
# students
#
# 创建新学⽣记录（学⽣编号s_id、学⽣班级（外键）c_id、学⽣姓名s_name、籍贯s_home、
# 毕业院校s_college、专业s_major、⼊学时间s_study_date、
# 毕业时间s_graduate_date、学历s_academic、
#
# 顾问编号sales_id、年龄s_age、性别s_gender）
# 指向: 成绩表 班级表

#学生表  - >  班级表     n  : 1  的关系
#在n  这边建立外键  指向班级表
class Students(Base):
    __tablename__ = "students"
    __table_args__ = {'extend_existing': True}   #解决重重复建表
    s_id = Column(Integer, primary_key=True,autoincrement=True)       #学生编号
    c_id =Column(Integer,ForeignKey('classes.c_id'))   # 学生班级
    s_name=Column(String(100))               #学生姓名
    s_home=Column(String(1000))              #学生籍贯
    s_college=Column(String(500))           #学生毕业院校
    s_major=Column(String(1000))           #学生专业
    s_study_date=Column(Date)               #入学时间
    s_graduate_date=Column(Date)           #毕业时间
    s_academic = Column(String(100))      #学历
    sales_id=Column(Integer,ForeignKey('teachers.t_id'))              #顾问编号
    s_age=Column(Integer)                  #年龄
    s_gender=Column(String(20))            #性别
    s_isdel=Column(Integer,default=0)              #学生是否删除  1：已删除  0：未删除

    classes=relationship('Classes',back_populates='students')  #建立 班级表建立关系  班级表：学生表=1:n
    grades = relationship('Grades', back_populates='students')   #与成绩表建立关系  成绩表：学生表= n:1
    offers = relationship('Offers', back_populates='students',uselist=False)  # 与工作表建立关系 工作表：学生表 = 1：1 uselist=False  告诉数据库这两个表是一对一关系
    teachers = relationship('Teachers', back_populates='students')