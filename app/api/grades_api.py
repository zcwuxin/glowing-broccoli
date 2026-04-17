from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query,Path
from app.dao import grades_dao
from app.scheme import grades_request,grades_response

grade_router = APIRouter()
security = HTTPBearer()


#修改成绩
@grade_router.patch('/grade/',response_model=grades_response.GradeRes,summary='修改学生成绩')
async def put_grade(update_grade:grades_request.OperateGrade,db= Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    res =grades_dao.put_grade(db,update_grade.s_id,update_grade.g_order,update_grade.g_score)
    if res:
        return {"code":200,"message":"修改成功，本次修改成绩详情如下","s_id":update_grade.s_id,
                "g_order":update_grade.g_order,"g_score":update_grade.g_score}
    else:
        raise HTTPException(status_code=404,detail="成绩不存在，请核实该学生是否有参加这次考试")

#删除成绩
@grade_router.delete('/grades',response_model=grades_response.GradeRes,summary='删除学生成绩')
async def post_delete_grade(delete_grade:grades_request.DeleteGrade,db= Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    res = grades_dao.remove_grade(db,delete_grade.s_id,delete_grade.g_order)
    if res:
        return {"code":204,"message":"删除成功！"}
    else:
        raise HTTPException(status_code=404,detail="成绩不存在，请核实该学生是否有参加这次考试")
# 查询成绩
@grade_router.get('/grades/{s_id}',summary='查询学生成绩')
async def get_grade(s_id:int=Path(description="学号")
                     ,g_order:int=Query(le=5,description="考试序次")
                     ,db= Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    res = grades_dao.get_grade(db,s_id,g_order)
    print(res)
    if not res:
        raise HTTPException(status_code=404,detail="学号和考试序次不匹配")
    else:
        return {"code":200,"message":f"学号：{s_id}，第{g_order}次考试成绩为{res[0]}"}

#添加成绩
@grade_router.post('/grades',response_model=grades_response.GradeRes,summary='添加学生成绩')
async def post_grade(add_grade:grades_request.OperateGrade,db= Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    res =grades_dao.post_grade(db,add_grade.s_id,add_grade.g_order,add_grade.g_score)
    if res:
        raise HTTPException(status_code=409,detail="成绩已存在")
    else:
        return {"code":201,"message":"添加成功，本次添加成绩详情如下",
                "s_id":add_grade.s_id,"g_order":add_grade.g_order,"g_score":add_grade.g_score}

