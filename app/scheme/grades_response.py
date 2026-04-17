from typing import Optional

from pydantic import BaseModel,Field

class GradeRes(BaseModel):
    code:int
    message:str
    s_id:Optional[int]=Field(None)
    g_order:Optional[int]=Field(None)
    g_score:Optional[float]=Field(None)