
from sqlalchemy import Column, Integer, String, Date, Float,ForeignKey
from sqlalchemy.orm import relationship
from app.core import Base
from sqlalchemy import DateTime

#**2.3** 学⽣就业管理模块  job

# 就业信息管理
#
# 记录学⽣就业状态（主键（ o_id ） 学⽣编号 外键（s_id)，就业开放时间o_open_date、
# offer下发时间o_send_date、就业公司名称o_company、就 业薪资o_salary）
# 就业表  与 学生表  1：1的关系
class Offers(Base):
    __tablename__ = "offers"
    o_id =Column(Integer,primary_key=True,autoincrement=True)      # 就业id  主键自增
    s_id=Column(Integer,ForeignKey('students.s_id'))               #学生ID  外键
    o_open_date=Column(DateTime)                             #就业开放时间
    o_send_date=Column(DateTime)                        #offer下发时间
    o_company= Column(String(200))                               # 就业公司
    o_salary=Column(Float)                                    #就业薪资
    o_isdel=Column(Integer,default=0)

    students = relationship('Students', back_populates='offers')  # 与学生表建立联系