from pydantic import BaseModel,Field
from datetime import datetime
from decimal import Decimal
from typing import Optional
class stu_info_front(BaseModel):
    s_id: Optional[int] = Field(None, ge=1, description="学生ID，必须为正整数")
    o_company: Optional[str] = Field(
        None,
        pattern=r'^[\u4e00-\u9fa5a-zA-Z0-9\s\-&]+$',  # 中英文、数字、空格、-、&
        max_length=200,
        description="公司名称"
    )
    o_salary: Optional[Decimal] = Field(None, ge=Decimal('0'), le=Decimal('99999999.99'), description="薪资")
    o_open_date:Optional[datetime]=None
    o_send_date:Optional[datetime]=None
class stu_info_del(BaseModel):#专为删除用
    o_id: int = Field(..., ge=1, description="Offer ID，必填且为正整数")
class stu_info_alter(stu_info_front):#专为修改用
    o_id: int = Field(..., ge=1, description="Offer ID，必填且为正整数")

