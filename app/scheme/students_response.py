from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List
from datetime import date
T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "操作成功"
    data: Optional[T] = None

class StudentInfo(BaseModel):
    s_id: int
    c_id: int
    s_name: str
    s_home: str
    s_college: str
    s_major: str
    s_study_date: date
    s_graduate_date: date
    s_academic: str
    sales_id: int
    s_age: int
    s_gender: str

    class Config:
        from_attributes = True





'''
响应体模型：
    WJC  建立
'''
class StudentsResponse(BaseModel):
    s_id:int=Field('',description='学生编号'),# = Column(Integer, primary_key=True)  # 学生编号
    c_id :int=Field(...,description='学生班级')  # 学生班级，这里是外键   外键未完成
    s_name:str=Field(...,description='学生姓名')# = Column(String(100))  # 学生姓名
    s_home:str=Field(...,description='学生籍贯')#  = Column(String(1000))  # 学生籍贯
    s_college:str=Field(...,description='学生毕业院校')#  = Column(String(500))  # 学生毕业院校
    s_major:str=Field(...,description='学生专业')#  = Column(String(1000))  # 学生专业
    s_study_date:date=Field(...,description='入学时间 YYYY-MM-DD',examples=['YYYY-MM-DD'])#  = Column(Date)  # 入学时间
    s_graduate_date:date=Field(...,description='毕业时间 YYYY-MM-DD',examples=['YYYY-MM-DD'])  # 毕业时间
    s_academic:str=Field(...,description='学生学历')# # 学历  正则表达式 对学历进行限制
    sales_id :int =Field(...,description='顾问编号') # 顾问编号
    s_age:int=Field(...,description='学生年龄')#  年龄
    s_gender:str=Field(...,description='性别',pattern=r'^男|女$')#性别  正则表达式

    # s_del:int=Field(1,description='学生编号')# = Column(Integer)  # 学生是否删除  1：已删除  0：未删除
