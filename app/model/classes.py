from sqlalchemy import Column, Integer, String,Date,ForeignKey
from sqlalchemy.orm import relationship
from app.core import Base

# **2.4** 班级管理模块
#
# 班级信息管理（班级编号c_id， 开课时间c_start_date， 班主任 授课⽼师 ）
#班级表
class Classes(Base):
    __tablename__ = "classes"
    c_id = Column(Integer,primary_key=True,index=True,autoincrement=True)      # 班级ID 自增主键
    c_name= Column(String(200))             # 班级名称
    c_start_date = Column(Date)                                      #开课时间
    c_isdel = Column(Integer,default=0)

    students = relationship('Students',back_populates='classes')    #与学生表建立联系
    # 两个外键列
    homeroom_teacher_id = Column(Integer, ForeignKey("teachers.t_id"))
    lead_teacher_id = Column(Integer, ForeignKey("teachers.t_id"))

    # 关系：使用 homeroom_teacher_id 连接
    homeroom_teacher = relationship(
        "Teachers",
        foreign_keys="Classes.homeroom_teacher_id",  # 明确指定使用这个外键
        back_populates="homeroom_classes",
        uselist=False  # 一个班级只有一个班主任
    )

    # 关系：使用 lead_teacher_id 连接
    lead_teacher = relationship(
        "Teachers",
        foreign_keys="Classes.lead_teacher_id",  # 明确指定使用这个外键
        back_populates="lead_classes",
        uselist=False
    )
    def __repr__(self):
        return f"<c_id: {self.c_id}, c_name: {self.c_name}, home_t_id: {self.homeroom_teacher_id}, lead_t_id: {self.lead_teacher_id}>"
