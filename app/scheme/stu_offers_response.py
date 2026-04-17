from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class stu_info_front(BaseModel):
    s_id:Optional[int]=None
    o_company:Optional[str]=None
    o_salary:Optional[float]=None
    o_open_date:Optional[datetime]=None
    o_send_date:Optional[datetime]=None
class stu_info_del(BaseModel):#专为删除用
    o_id:int

