
from pydantic import BaseModel,Field,field_validator
from datetime import date, datetime

# 定义可选请求体模型
class ClassUpdate(BaseModel):
    """班级基础信息，用于数据验证"""
    course_name: str = Field(None, description="课程/班级名称")
    c_head_teachers: str = Field(None, description="班主任")
    teacher_name: str = Field(None, description="班主任/授课老师")
    c_start_date: str = Field(None, description="开课时间（格式：YYYY-MM-DD）")
    s_isdel:int = Field(None, description="是否删除")

    # 校验日期格式
    @field_validator('c_start_date')
    def validate_date(cls, v):
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("日期格式错误，需为YYYY-MM-DD")

