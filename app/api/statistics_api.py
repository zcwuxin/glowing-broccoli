from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.database import get_db
from fastapi import APIRouter,Depends,HTTPException,Query
from ..dao import statistics_dao


statistics_router=APIRouter()
security = HTTPBearer()
# ==========================  2.6.3 就业统计相关接口  =================================================
####统计就业薪资最⾼的前五名学⽣的姓名，班级和就业时间(拿到offer的时间)，就业公司
@statistics_router.get('/offers/classes',summary='统计就业薪资最⾼的前五名学⽣')
async def salary_top5(db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    return statistics_dao.top5_salary_students(db)

#####统计每个学⽣的就业时⻓（offer下发时间-就业开放时间)
@statistics_router.get('/offers/',summary='统计每个学⽣的就业时⻓')
async def job_duration_days(db=Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    result = statistics_dao.student_job_duration(db)
    # 如果没有数据，返回明确提示，不会空白
    if not result:
        return {"code": 200, "msg": "暂无就业数据", "data": []}

    return {"code": 200, "msg": "查询成功", "data": result}