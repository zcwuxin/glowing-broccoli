from fastapi import Query
from pydantic import BaseModel
from typing import Optional
from pydantic import Field
from datetime import date

class StudentsRequest(BaseModel):
    c_id: int = Field(..., description="学生班级")
    s_name: str = Field(..., description="学生姓名")
    s_home: str = Field(..., description="学生籍贯")
    s_college: str = Field(..., description="学生毕业院校")
    s_major: str = Field(..., description="学生专业")
    s_study_date:date = Field(..., description="入学时间")  # 改成 str
    s_graduate_date: date = Field(..., description="毕业时间") # 改成 str
    s_academic: str = Field(..., description="学生学历")
    sales_id: int = Field(..., description="顾问编号")
    s_age: int = Field(..., description="学生年龄")
    s_gender: str = Field(..., description="性别 男/女") # 改成 str

class StudentsQueryRequest(BaseModel):
    s_id: Optional[int] = None
    c_id: Optional[int] = None
    s_name: Optional[str] = None
    s_home: Optional[str] = None
    s_college: Optional[str] = None
    s_major: Optional[str] = None
    s_study_date_start: Optional[date] = None
    s_study_date_end: Optional[date] = None
    s_graduate_date_before: Optional[date] = None
    s_graduate_date_after: Optional[date] = None
    s_academic: Optional[str] = None
    sales_id: Optional[int] = None
    s_age_min: Optional[int] = None
    s_age_max: Optional[int] = None
    s_gender: Optional[str] = None
    s_del: Optional[int] = 0


class StudentsRequestWJC(BaseModel):
    # s_id:int=Field('',description='学生编号'),# = Column(Integer, primary_key=True)  # 学生编号
    c_id: int = Field(..., description='学生班级')  # 学生班级，这里是外键   外键未完成
    s_name: str = Field(..., description='学生姓名')  # = Column(String(100))  # 学生姓名
    s_home: str = Field(..., description='学生籍贯')  # = Column(String(1000))  # 学生籍贯
    s_college: str = Field(..., description='学生毕业院校')  # = Column(String(500))  # 学生毕业院校
    s_major: str = Field(..., description='学生专业')  # =     Column(String(1000))  # 学生专业
    s_study_date: date = Field(..., description='入学开始时间 YYYY-MM-DD', examples=['YYYY-MM-DD'])  # = Column(Date)  # 入学时间
    s_graduate_date: date = Field(..., description='毕业时间 YYYY-MM-DD', examples=['YYYY-MM-DD'])  # 毕业时间
    s_academic: str = Field(..., description='学生学历')  # # 学历   正则表达式 对学历进行限制
    sales_id: int = Field(..., description='顾问编号')  # 顾问编号
    s_age: int = Field(..., description='学生年龄')  # 年龄
    s_gender: str = Field(..., description='性别',pattern=r'^男|女$')  # 性别  正则表达式

    # s_del:int=Field(1,description='学生编号')# = Column(Integer)  # 学生是否删除  1：已删除  0：未删除


''''
学生请求体查询模型;
    WJC 建立
'''


# 查询的时候，支持部分参数写，部分参数不写
class StudentsQueryRequestWJC(BaseModel):
    """用于查询的学生请求模型"""
    s_id: Optional[int] = Field(None, description="学生ID")
    c_id: Optional[int] = Field(None, description="班级ID")
    s_name: Optional[str] = Field(None, description="学生姓名（支持模糊）")
    s_home: Optional[str] = Field(None, description="籍贯（支持模糊）")
    s_college: Optional[str] = Field(None, description="毕业院校")
    s_major: Optional[str] = Field(None, description="专业")

    s_study_date_start: Optional[date] = Field(None, description="入学开始时间 YYYY-MM-DD")
    s_study_date_end: Optional[date] = Field(None, description="毕业结束时间 YYYY-MM-DD")
    s_graduate_date_before: Optional[date] = Field(None, description="毕业时间之前 YYYY-MM-DD")
    s_graduate_date_after: Optional[date] = Field(None, description="毕业时间之后 YYYY-MM-DD")

    s_academic: Optional[str] = Field(None, description="学历")

    sales_id: Optional[int] = Field(None, description="顾问ID")
    s_age_min: Optional[int] = Field(None, description="最小年龄")
    s_age_max: Optional[int] = Field(None, description="最大年龄")
    s_gender: Optional[str] = Field(None, description="性别")
    s_isdel: Optional[int] = Field(0, description="是否删除 0:否 1:是")


'''
简单记忆：Optional[str] = 这个参数“可以有，也可以没有”，没有就是 None。

# 使用 Optional
class StudentsQueryRequest(BaseModel):
    s_name: Optional[str] = Field(None, description="学生姓名")
    s_age_min: Optional[int] = Field(None, description="最小年龄")

# 如果不使用 Optional
class StudentsQueryRequest(BaseModel):
    s_name: str = Field(None, description="学生姓名")  # ⚠️ 类型不匹配
    # str 类型不能赋值为 None，Pydantic 会报错或自动转换

场景2：如果不使用 Optional
    python
    class StudentsQueryRequest(BaseModel):
        s_name: str = Field(...)  # 必填！
        s_age: int = Field(...)   # 必填！

    # 客户端必须传所有参数，否则报错：
    GET /students?s_name=张三  



'''

from typing import Annotated


# 创建一个辅助函数，从模型中提取字段信息并生成查询参数   如果没有这个  再先文档没有文字提示
def get_student_query_params(
        s_id: Annotated[Optional[int], Query(description=StudentsQueryRequestWJC.model_fields['s_id'].description)] = None,
        c_id: Annotated[Optional[int], Query(description=StudentsQueryRequestWJC.model_fields['c_id'].description)] = None,
        s_name: Annotated[
            Optional[str], Query(description=StudentsQueryRequestWJC.model_fields['s_name'].description)] = None,
        s_home: Annotated[
            Optional[str], Query(description=StudentsQueryRequestWJC.model_fields['s_home'].description)] = None,
        s_college: Annotated[
            Optional[str], Query(description=StudentsQueryRequestWJC.model_fields['s_college'].description)] = None,
        s_major: Annotated[
            Optional[str], Query(description=StudentsQueryRequestWJC.model_fields['s_major'].description)] = None,
        s_study_date_start: Annotated[Optional[date], Query(
            description=StudentsQueryRequestWJC.model_fields['s_study_date_start'].description)] = None,
        s_study_date_end: Annotated[Optional[date], Query(
            description=StudentsQueryRequestWJC.model_fields['s_study_date_end'].description)] = None,
        s_graduate_date_before: Annotated[Optional[date], Query(
            description=StudentsQueryRequestWJC.model_fields['s_graduate_date_before'].description)] = None,
        s_graduate_date_after: Annotated[Optional[date], Query(
            description=StudentsQueryRequestWJC.model_fields['s_graduate_date_after'].description)] = None,
        s_academic: Annotated[
            Optional[str], Query(description=StudentsQueryRequestWJC.model_fields['s_academic'].description)] = None,
        sales_id: Annotated[
            Optional[int], Query(description=StudentsQueryRequestWJC.model_fields['sales_id'].description)] = None,
        s_age_min: Annotated[
            Optional[int], Query(description=StudentsQueryRequestWJC.model_fields['s_age_min'].description)] = None,
        s_age_max: Annotated[
            Optional[int], Query(description=StudentsQueryRequestWJC.model_fields['s_age_max'].description)] = None,
        s_gender: Annotated[
            Optional[str], Query(description=StudentsQueryRequestWJC.model_fields['s_gender'].description)] = None,
        s_isdel: Annotated[Optional[int], Query(description=StudentsQueryRequestWJC.model_fields['s_isdel'].description)] = 0,
):
    """创建查询参数对象"""
    return StudentsQueryRequestWJC(
        s_id=s_id,
        c_id=c_id,
        s_name=s_name,
        s_home=s_home,
        s_college=s_college,
        s_major=s_major,
        s_study_date_start=s_study_date_start,
        s_study_date_end=s_study_date_end,
        s_graduate_date_before=s_graduate_date_before,
        s_graduate_date_after=s_graduate_date_after,
        s_academic=s_academic,
        sales_id=sales_id,
        s_age_min=s_age_min,
        s_age_max=s_age_max,
        s_gender=s_gender,
        s_isdel=s_isdel,
    )


'''
Annotated - "给类型贴标签"
  Annotated[int, Query(...)] 表示:
        "这是一个 int，但它还附带一些额外信息（比如如何从请求中读取）

# 没有 Annotated
def get_student(
    s_name: str = Query(None, description="学生姓名")
):  # 类型和验证分开写


# Annotated 写法
def get_student(
    s_name: Annotated[str, Query(description="学生姓名")] = None
):  # 类型和验证写在一起，更清晰


StudentsQueryRequest.model_fields 是一个字典，包含模型中所有字段的元信息
'''
