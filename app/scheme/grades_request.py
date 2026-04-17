from pydantic import BaseModel,Field
from typing import Literal


# 给新增、修改成绩用
class OperateGrade(BaseModel):
    s_id: int=Field(description="学号")
    g_order: int=Field(...,le=5,description="考试序次")
    g_score: float=Field(...,ge=0,le=100,description="分数")

# 给删除成绩用
class DeleteGrade(BaseModel):
    s_id: int=Field(description="学号")
    g_order: int=Field(...,le=5,description="考试序次")

#给grade/sta1接口用的
# 查询每次考试成绩都在80分以上的学⽣的编号，姓名和成绩
# class GradeSta1(BaseModel):
#     score:float=Field(le=100,description="分数标准")




# 查询有两次以上不及格的学⽣的姓名，班级和不及格成