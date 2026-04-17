from sqlalchemy import Column, Integer, String,Date
from sqlalchemy.orm import relationship
from app.core import Base
from . import classes

class Teachers(Base):
    __tablename__ = 'teachers'
    t_id = Column(Integer,primary_key=True,index=True,autoincrement=True)   #老师编号
    t_name = Column(String(100),nullable=False)     #老师姓名
    t_gender = Column(String(50))   #老师性别
    t_hire_date = Column(Date)   #老师入职日期
    t_isdel = Column(Integer,default=0)

    students = relationship('Students', back_populates='teachers')  # 与学生表建立联系

    # 反向关系：一个老师可以担任多个班级的班主任
    homeroom_classes = relationship(
        "Classes",
        foreign_keys="Classes.homeroom_teacher_id",  # 指定使用 Classes 表中的哪个外键
        back_populates="homeroom_teacher"
    )

    # 反向关系：一个老师可以担任多个班级的授课老师
    lead_classes = relationship(
        "Classes",
        foreign_keys='Classes.lead_teacher_id',
        back_populates="lead_teacher"
    )
    def __repr__(self):
        return f"<t_id: {self.t_id}, t_name: {self.t_name}, home_classes: {self.homeroom_classes}, lead_classes: {self.lead_classes}>"
