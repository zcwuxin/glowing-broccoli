
from pydantic import BaseModel, Field,field_serializer
from datetime import datetime, date
from typing import Optional, List
'''
统计模块：
    每个班级人数及男女生人数统计响应
    
'''


"""
每个班级的人数及男女生人数统计响应
    WJC 建立
"""
class ClassStatisticsResponse(BaseModel):

    c_id: int = Field(..., description="班级ID")
    c_name: Optional[str] = Field(None, description="班级名称")
    total_students: int = Field(..., description="班级总人数")
    male_count: int = Field(..., description="男生人数")
    female_count: int = Field(..., description="女生人数")



"""
超过30岁的学生信息响应
    WJC 建立
"""
class StudentAgeResponse(BaseModel):
    s_id: int = Field(..., description="学生编号")
    s_name: str = Field(..., description="学生姓名")
    s_age: int = Field(..., description="学生年龄")
    s_gender: int = Field(..., description="性别 0:女 1:男")
    c_id: int = Field(..., description="班级ID")
    s_home: Optional[str] = Field(None, description="籍贯")
    s_college: Optional[str] = Field(None, description="毕业院校")


class ScoreItem(BaseModel):
    """单次不及格成绩项"""
    g_order: int = Field(..., description="考试次序")
    g_score: float = Field(..., description="考试分数")


class FailStudentResponse(BaseModel):
    """有两次以上不及格的学生响应"""
    s_id: int = Field(..., description="学生编号")
    s_name: str = Field(..., description="学生姓名")
    c_id: int = Field(..., description="班级ID")
    c_name: str = Field(..., description='班级名称')
    # g_order: int = Field(..., description="考试次序")
    # g_score: float = Field(..., description="不及格成绩列表")
    g_order_count: List[ScoreItem] = Field(..., description='考试次序：考试成绩')


class AvgScores(BaseModel):
    g_order: int = Field(..., description='考试次序'),
    class_avg_score: float = Field(..., description='班级每次考试的平均分')


    #给JSON做序列化
    #当路由函数return返回数据的时候，fastapi会把python对象转换为字符串发送前端
    #在这个转换的过程中field_serializer会被触发
    @field_serializer("class_avg_score")
    def avg_score(self,value:float)->float:
        return round(value,2)



class ClassAvgScoreResponse(BaseModel):
    """每次考试每个班级的平均分响应"""
    c_id: int = Field(..., description="班级ID")
    c_name: Optional[str] = Field(None, description="班级名称")
    avg_score_count: List[AvgScores] = Field(..., description="班级考试序次：每次平均分")